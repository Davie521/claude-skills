---
name: swiftui-patterns
description: SwiftUI architecture patterns, state management with @Observable, view composition, navigation, actor-based persistence, protocol-based DI for testing, performance optimization, and modern iOS/macOS UI best practices.
---

# SwiftUI Patterns

Modern SwiftUI patterns for building declarative, performant user interfaces on Apple platforms. Covers the Observation framework, view composition, type-safe navigation, and performance optimization.

## When to Activate

- Building SwiftUI views and managing state (`@State`, `@Observable`, `@Binding`)
- Designing navigation flows with `NavigationStack`
- Structuring view models and data flow
- Optimizing rendering performance for lists and complex layouts
- Working with environment values and dependency injection in SwiftUI
- Building a thread-safe local persistence layer with actors
- Making code testable by mocking file system / network boundaries behind protocols

## State Management

### Property Wrapper Selection

Choose the simplest wrapper that fits:

| Wrapper | Use Case |
|---------|----------|
| `@State` | View-local value types (toggles, form fields, sheet presentation) |
| `@Binding` | Two-way reference to parent's `@State` |
| `@Observable` class + `@State` | Owned model with multiple properties |
| `@Observable` class (no wrapper) | Read-only reference passed from parent |
| `@Bindable` | Two-way binding to an `@Observable` property |
| `@Environment` | Shared dependencies injected via `.environment()` |

### @Observable ViewModel

Use `@Observable` (not `ObservableObject`) — it tracks property-level changes so SwiftUI only re-renders views that read the changed property:

```swift
@Observable
final class ItemListViewModel {
    private(set) var items: [Item] = []
    private(set) var isLoading = false
    var searchText = ""

    private let repository: any ItemRepository

    init(repository: any ItemRepository = DefaultItemRepository()) {
        self.repository = repository
    }

    func load() async {
        isLoading = true
        defer { isLoading = false }
        items = (try? await repository.fetchAll()) ?? []
    }
}
```

### View Consuming the ViewModel

```swift
struct ItemListView: View {
    @State private var viewModel: ItemListViewModel

    init(viewModel: ItemListViewModel = ItemListViewModel()) {
        _viewModel = State(initialValue: viewModel)
    }

    var body: some View {
        List(viewModel.items) { item in
            ItemRow(item: item)
        }
        .searchable(text: $viewModel.searchText)
        .overlay { if viewModel.isLoading { ProgressView() } }
        .task { await viewModel.load() }
    }
}
```

### Environment Injection

Replace `@EnvironmentObject` with `@Environment`:

```swift
// Inject
ContentView()
    .environment(authManager)

// Consume
struct ProfileView: View {
    @Environment(AuthManager.self) private var auth

    var body: some View {
        Text(auth.currentUser?.name ?? "Guest")
    }
}
```

## View Composition

### Extract Subviews to Limit Invalidation

Break views into small, focused structs. When state changes, only the subview reading that state re-renders:

```swift
struct OrderView: View {
    @State private var viewModel = OrderViewModel()

    var body: some View {
        VStack {
            OrderHeader(title: viewModel.title)
            OrderItemList(items: viewModel.items)
            OrderTotal(total: viewModel.total)
        }
    }
}
```

### ViewModifier for Reusable Styling

```swift
struct CardModifier: ViewModifier {
    func body(content: Content) -> some View {
        content
            .padding()
            .background(.regularMaterial)
            .clipShape(RoundedRectangle(cornerRadius: 12))
    }
}

extension View {
    func cardStyle() -> some View {
        modifier(CardModifier())
    }
}
```

## Navigation

### Type-Safe NavigationStack

Use `NavigationStack` with `NavigationPath` for programmatic, type-safe routing:

```swift
@Observable
final class Router {
    var path = NavigationPath()

    func navigate(to destination: Destination) {
        path.append(destination)
    }

    func popToRoot() {
        path = NavigationPath()
    }
}

enum Destination: Hashable {
    case detail(Item.ID)
    case settings
    case profile(User.ID)
}

struct RootView: View {
    @State private var router = Router()

    var body: some View {
        NavigationStack(path: $router.path) {
            HomeView()
                .navigationDestination(for: Destination.self) { dest in
                    switch dest {
                    case .detail(let id): ItemDetailView(itemID: id)
                    case .settings: SettingsView()
                    case .profile(let id): ProfileView(userID: id)
                    }
                }
        }
        .environment(router)
    }
}
```

## Architecture Patterns

### Actor-Based Local Persistence

For local storage behind a ViewModel, use an actor: compiler-enforced thread safety (no locks or `DispatchQueue`), an in-memory dictionary cache for O(1) reads, and atomic file writes for durability.

```swift
public actor LocalRepository<T: Codable & Identifiable> where T.ID == String {
    private var cache: [String: T] = [:]
    private let fileURL: URL

    public init(directory: URL = .documentsDirectory, filename: String = "data.json") {
        self.fileURL = directory.appendingPathComponent(filename)
        self.cache = Self.load(from: fileURL) // sync load OK: actor isolation not active in init
    }

    public func save(_ item: T) throws {
        cache[item.id] = item
        try persist()
    }

    public func delete(_ id: String) throws {
        cache[id] = nil
        try persist()
    }

    public func find(by id: String) -> T? { cache[id] }
    public func loadAll() -> [T] { Array(cache.values) }

    private func persist() throws {
        let data = try JSONEncoder().encode(Array(cache.values))
        try data.write(to: fileURL, options: .atomic) // .atomic: no partial writes on crash
    }

    private static func load(from url: URL) -> [String: T] {
        guard let data = try? Data(contentsOf: url),
              let items = try? JSONDecoder().decode([T].self, from: data) else { return [:] }
        return Dictionary(uniqueKeysWithValues: items.map { ($0.id, $0) })
    }
}
```

All calls are `await` from outside the actor (`try await repository.save(item)`). Pair with an `@Observable` ViewModel that calls `loadAll()` after each mutation. Types crossing the actor boundary must be `Sendable`; don't use `nonisolated` to bypass isolation.

> **Scaling caveat**: every `save`/`delete` re-encodes and rewrites the *entire* dataset — O(n) per write. This is fine for small datasets with infrequent writes (settings, a few hundred records). For high-frequency writes or large/growing datasets, use SQLite (e.g. GRDB) or SwiftData instead of this whole-file pattern.

### Protocol-Based DI for Testing

Abstract each external boundary (file system, network, iCloud) behind one small, `Sendable` protocol — never a god protocol. Production code uses default parameters; tests inject mocks with configurable errors to exercise failure paths deterministically.

```swift
// One protocol per external concern
public protocol FileAccessorProviding: Sendable {
    func read(from url: URL) throws -> Data
    func write(_ data: Data, to url: URL) throws
}

public struct DefaultFileAccessor: FileAccessorProviding {
    public init() {}
    public func read(from url: URL) throws -> Data { try Data(contentsOf: url) }
    public func write(_ data: Data, to url: URL) throws { try data.write(to: url, options: .atomic) }
}

// Mock with configurable errors for failure-path tests
public final class MockFileAccessor: FileAccessorProviding, @unchecked Sendable {
    public var files: [URL: Data] = [:]
    public var readError: Error?

    public init() {}

    public func read(from url: URL) throws -> Data {
        if let error = readError { throw error }
        guard let data = files[url] else { throw CocoaError(.fileReadNoSuchFile) }
        return data
    }

    public func write(_ data: Data, to url: URL) throws { files[url] = data }
}

// Consumer: defaults for production, injection for tests
public enum SyncError: Error { case dataUnreadable }

public actor SyncManager {
    private let fileAccessor: FileAccessorProviding
    private let dataURL: URL

    public init(fileAccessor: FileAccessorProviding = DefaultFileAccessor(),
                dataURL: URL = URL.documentsDirectory.appendingPathComponent("data.json")) {
        self.fileAccessor = fileAccessor
        self.dataURL = dataURL
    }

    public func loadData() throws -> Data {
        do { return try fileAccessor.read(from: dataURL) }
        catch { throw SyncError.dataUnreadable }
    }
}
```

Tests with Swift Testing:

```swift
import Testing

@Test("loadData returns stored data")
func loadData() async throws {
    let url = URL(filePath: "/data.json")
    let mock = MockFileAccessor()
    mock.files[url] = Data("hello".utf8)

    let manager = SyncManager(fileAccessor: mock, dataURL: url)
    let result = try await manager.loadData()
    #expect(result == Data("hello".utf8))
}

@Test("loadData surfaces read failures as SyncError")
func loadDataError() async {
    let mock = MockFileAccessor()
    mock.readError = CocoaError(.fileReadCorruptFile)

    let manager = SyncManager(fileAccessor: mock, dataURL: URL(filePath: "/data.json"))
    await #expect(throws: SyncError.self) { try await manager.loadData() }
}
```

Only mock boundaries — types with no external dependencies need no protocol. Avoid `#if DEBUG` conditionals in place of injection.

## Performance

### Use Lazy Containers for Large Collections

`LazyVStack` and `LazyHStack` create views only when visible:

```swift
ScrollView {
    LazyVStack(spacing: 8) {
        ForEach(items) { item in
            ItemRow(item: item)
        }
    }
}
```

### Stable Identifiers

Always use stable, unique IDs in `ForEach` — avoid using array indices:

```swift
// Use Identifiable conformance or explicit id
ForEach(items, id: \.stableID) { item in
    ItemRow(item: item)
}
```

### Avoid Expensive Work in body

- Never perform I/O, network calls, or heavy computation inside `body`
- Use `.task {}` for async work — it cancels automatically when the view disappears
- Use `.sensoryFeedback()` and `.geometryGroup()` sparingly in scroll views
- Minimize `.shadow()`, `.blur()`, and `.mask()` in lists — they trigger offscreen rendering

### Equatable Conformance

For views with expensive bodies, conform to `Equatable` to skip unnecessary re-renders:

```swift
struct ExpensiveChartView: View, Equatable {
    let dataPoints: [DataPoint] // DataPoint must conform to Equatable

    static func == (lhs: Self, rhs: Self) -> Bool {
        lhs.dataPoints == rhs.dataPoints
    }

    var body: some View {
        // Complex chart rendering
    }
}
```

## Previews

Use `#Preview` macro with inline mock data for fast iteration:

```swift
#Preview("Empty state") {
    ItemListView(viewModel: ItemListViewModel(repository: EmptyMockRepository()))
}

#Preview("Loaded") {
    ItemListView(viewModel: ItemListViewModel(repository: PopulatedMockRepository()))
}
```

## Anti-Patterns to Avoid

- Using `ObservableObject` / `@Published` / `@StateObject` / `@EnvironmentObject` in new code — migrate to `@Observable`
- Putting async work directly in `body` or `init` — use `.task {}` or explicit load methods
- Creating view models as `@State` inside child views that don't own the data — pass from parent instead
- Using `AnyView` type erasure — prefer `@ViewBuilder` or `Group` for conditional views
- Ignoring `Sendable` requirements when passing data to/from actors
