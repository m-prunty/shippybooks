# shippybooks

See [ABOUT.md](ABOUT.md) for the project overview, architecture, and motivation.

## Project documentation

- [Architecture and API overview](ABOUT.md)
- [Class, project, and control-flow diagrams](diagrams/README.md)
- [Current implementation handoff](HANDOFF.md)

## Diagrams

### Class diagram

The class diagram shows the domain model, commands, queries, events, repositories, handlers, notification layer, and application wiring. Generated from `src/shippybooks` with `pyreverse` (Pylint). Source at `diagrams/classes.mmd`.

```mermaid
classDiagram
    %% ----------------------------------------------------------------
    %% Domain model (src/shippybooks/domain/models.py)
    %% ----------------------------------------------------------------
    class OrderStatus {
        <<enumeration>>
        PENDING
        PROCESSING
        SHIPPED
        CANCELLED
    }
    class Book {
        +id: str
        +title: str
        +author: str
        +price: float
        +stock: int
        +update_stock(quantity: int): None
    }
    class OrderItem {
        +book_id: str
        +quantity: int
    }
    class Order {
        +id: str
        +items: list[OrderItem]
        +timestamp: datetime
        +last_updated: datetime
        +status: OrderStatus
        +total: float
        +add_item(book: Book, quantity: int): None
        +change_status(new_status: OrderStatus): None
    }
    Book "1" *-- "many" OrderItem : contains
    Order "1" *-- "many" OrderItem : contains
    Order ..> OrderStatus : status

    %% ----------------------------------------------------------------
    %% Commands (src/shippybooks/domain/commands.py)
    %% ----------------------------------------------------------------
    class Command {
        <<frozen, abstract>>
        model_config = ConfigDict(frozen=True)
    }
    class CreateBook {
        +id: str
        +title: str
        +author: str
        +price: float
        +stock: int
    }
    class UpdateBookStock {
        +id: str
        +quantity: int
    }
    class CreateOrder {
        +id: str
        +items: list[OrderItem]
    }
    class ChangeOrderStatus {
        +id: str
        +new_status: OrderStatus
    }
    Command <|-- CreateBook
    Command <|-- UpdateBookStock
    Command <|-- CreateOrder
    Command <|-- ChangeOrderStatus
    CreateOrder ..> OrderItem : items

    %% ----------------------------------------------------------------
    %% Queries (src/shippybooks/domain/queries.py)
    %% ----------------------------------------------------------------
    class Query {
        <<frozen, abstract>>
    }
    class GetBook {
        +id: str
    }
    class ListBooks
    class GetOrder {
        +id: str
    }
    class ListOrders
    Query <|-- GetBook
    Query <|-- ListBooks
    Query <|-- GetOrder
    Query <|-- ListOrders

    %% ----------------------------------------------------------------
    %% Domain events (src/shippybooks/domain/events.py)
    %% ----------------------------------------------------------------
    class DomainEvent {
        <<abstract>>
    }
    class BookCreated {
        +book: Book
    }
    class BookUpdated {
        +book: Book
    }
    class OrderCreated {
        +order: Order
    }
    class OrderStatusChanged {
        +order_id: str
        +old_status: OrderStatus
        +new_status: OrderStatus
    }
    DomainEvent <|-- BookCreated
    DomainEvent <|-- BookUpdated
    DomainEvent <|-- OrderCreated
    DomainEvent <|-- OrderStatusChanged

    %% ----------------------------------------------------------------
    %% Command handler (src/shippybooks/services/command_handlers.py)
    %% ----------------------------------------------------------------
    class CommandHandler {
        -event_bus: EventBus
        -book_repo: BookRepository
        -order_repo: OrderRepository
        +handle(command: Command): None
    }
    CommandHandler --> EventBus : publishes events
    CommandHandler --> BookRepository
    CommandHandler --> OrderRepository
    CommandHandler ..> CreateBook : handles
    CommandHandler ..> UpdateBookStock : handles
    CommandHandler ..> CreateOrder : handles
    CommandHandler ..> ChangeOrderStatus : handles

    %% ----------------------------------------------------------------
    %% Query handler (src/shippybooks/services/query_handlers.py)
    %% ----------------------------------------------------------------
    class QueryHandler {
        -book_repo: BookRepository
        -order_repo: OrderRepository
        +handle(query: Query): Any
    }
    QueryHandler --> BookRepository
    QueryHandler --> OrderRepository

    %% ----------------------------------------------------------------
    %% Repositories (src/shippybooks/services/repos.py)
    %% ----------------------------------------------------------------
    class BookRepository {
        -_books: dict[str, Book]
        +get(id: str): Book
        +save(book: Book): None
        +all(): list[Book]
    }
    class OrderRepository {
        -_orders: dict[str, Order]
        +get(id: str): Order
        +save(order: Order): None
        +all(): list[Order]
    }
    BookRepository --> Book : manages
    OrderRepository --> Order : manages
    BookRepository ..> BookORM : persists via ORM (optional)
    OrderRepository ..> OrderORM : persists via ORM (optional)

    %% ----------------------------------------------------------------
    %% ORM models (src/shippybooks/db/models.py)
    %% ----------------------------------------------------------------
    class BookORM {
        +id: str (PK)
        +title: str
        +author: str
        +price: float
        +stock: int
    }
    class OrderORM {
        +id: str (PK)
        +timestamp: datetime
        +status: str
        +total: float
        +items: list[OrderItemORM]
    }
    class OrderItemORM {
        +id: int (PK)
        +order_id: str (FK)
        +book_id: str (FK)
        +quantity: int
    }
    OrderORM "1" *-- "many" OrderItemORM : items

    %% ----------------------------------------------------------------
    %% Event bus (src/shippybooks/events/bus.py)
    %% ----------------------------------------------------------------
    class EventBus {
        -_subscribers: dict[type[DomainEvent], list]
        +subscribe(event_type, handler): None
        +publish(event: DomainEvent): None
    }
    EventBus --> DomainEvent : subscribes to

    %% ----------------------------------------------------------------
    %% Notification layer (src/shippybooks/events/notifications.py)
    %% ----------------------------------------------------------------
    class Notification {
        <<abstract, frozen>>
        +to_event(): dict[str, Any]
    }
    class BookNotification {
        +book_id: str
        +status: str
        +stock: int
    }
    class OrderConfirmation {
        +order_id: str
        +total: float
    }
    class StockAlert {
        +book_id: str
        +current_stock: int
    }
    class StatusUpdate {
        +order_id: str
        +new_status: OrderStatus
    }
    class Message {
        <<StrEnum>>
        BOOK_NOTIFICATION
        ORDER_CONFIRMATION
        STOCK_ALERT
        STATUS_UPDATE
    }
    Notification <|-- BookNotification
    Notification <|-- OrderConfirmation
    Notification <|-- StockAlert
    Notification <|-- StatusUpdate

    class NotificationHandler {
        -_handlers: dict
        +register(notify_type, handler): None
        +dispatch(notification: Notification): None
    }
    class NotificationDispatcher {
        -handler: NotificationHandler
        +on_book_created(e): None
        +on_book_updated(e): None
        +on_order_created(e): None
        +on_status_changed(e): None
    }
    class NotificationStore {
        -_events: list[dict]
        +append(notification): None
        +since(last_id: int): list[dict]
    }
    NotificationDispatcher --> NotificationHandler
    NotificationDispatcher --> BookNotification
    NotificationDispatcher --> StockAlert
    NotificationDispatcher --> OrderConfirmation
    NotificationDispatcher --> StatusUpdate
    NotificationHandler --> NotificationStore : append
    EventBus --> NotificationDispatcher : calls on_*()

    %% ----------------------------------------------------------------
    %% Application wiring (bootstrap.py, main.py, settings.py)
    %% ----------------------------------------------------------------
    class AppState {
        +cmd_handler: CommandHandler
        +query_handler: QueryHandler
        +notification_store: NotificationStore
    }
    class settings {
        +database_url: str
        +environment: str
        +persistent_memory: bool
    }
    class create_app {
        +builds the FastAPI application
    }
    AppState --> CommandHandler
    AppState --> QueryHandler
    AppState --> NotificationStore
```

View the rendered image: [diagrams/classes.png](diagrams/classes.png)

### Project diagram

The project diagram shows the `shippybooks` package structure, external dependencies, and runtime request flow between modules. Source at `diagrams/project.mmd`.

```mermaid
graph TD
    %% ----------------------------------------------------------------
    %% Project structure diagram for shippybooks
    %% ----------------------------------------------------------------
    subgraph shippybooks ["shippybooks package"]
        direction TB

        subgraph domain ["domain/"]
            models["models.py
Book, Order, OrderItem,
OrderStatus"]
            commands["commands.py
Command hierarchy"]
            queries["queries.py
Query hierarchy"]
            devents["events.py
DomainEvent hierarchy"]
        end

        subgraph services ["services/"]
            ch["command_handlers.py
CommandHandler"]
            qh["query_handlers.py
QueryHandler"]
            repos["repos.py
BookRepository, OrderRepository"]
        end

        subgraph events ["events/"]
            bus["bus.py
EventBus"]
            notif["notifications.py
NotificationDispatcher,
Notification types"]
            store["store.py
NotificationStore"]
        end

        subgraph api ["api/"]
            ep["endpoints/
books.py · orders.py
notifications.py · health.py"]
            deps["dependencies.py
FastAPI Depends wiring"]
        end

        subgraph db ["db/"]
            orm["models.py
SQLAlchemy ORM models"]
            sess["session.py
engine, get_session()"]
            base["base.py
Base, make_engine()"]
        end

        bootstrap["bootstrap.py
build_app_state()"]
        main["main.py
create_app() · uvicorn entry"]
        settings["settings.py
Settings
(pydantic-settings)"]
    end

    subgraph external ["External dependencies"]
        fastapi["FastAPI
web framework"]
        sqlalchemy["SQLAlchemy
ORM / SQLite"]
        pydantic["Pydantic
settings & models"]
        uvicorn["uvicorn
ASGI server"]
    end

    %% Runtime request flow
    client[("HTTP client")] --> ep
    ep --> deps
    deps --> ch
    deps --> qh
    bootstrap --> ch
    bootstrap --> qh
    bootstrap --> store
    main --> bootstrap
    main --> settings

    %% Command side
    ch --> repos
    ch --> bus
    qh --> repos
    repos --> orm
    orm --> sess

    %% Event-driven notifications
    bus --> notif
    notif --> store
```

View the rendered image: [diagrams/project.png](diagrams/project.png)

### Control flow diagram

The control flow diagram shows the write path (commands), query path (reads), health probe path, event-driven notifications, and optional persistence. Rendered from `diagrams/control-flow.dot` with Graphviz `dot`. Source at `diagrams/control-flow.mmd`.

```mermaid
flowchart TD
    %% ----------------------------------------------------------------
    %% Control flow diagram for shippybooks
    %% Mirrors diagrams/control-flow.dot
    %% ----------------------------------------------------------------
    classDef default fill:#e8f0fe,stroke:#1d4ed8,stroke-width:1px
    classDef command fill:#fef2f2,stroke:#ef4444,stroke-width:1px
    classDef query fill:#f0f9ff,stroke:#0284c7,stroke-width:1px
    classDef db fill:#f0fdf4,stroke:#16a34a,stroke-width:1px
    classDef event fill:#fffbeb,stroke:#d97706,stroke-width:1px

    Client(("HTTP client"))

    subgraph API ["FastAPI HTTP layer"]
        Endpoints["api/endpoints/
books.py · orders.py
notifications.py · health.py"]
        Deps["api/dependencies.py
Depends wiring"]
    end

    Main["main.py
create_app()"]
    Bootstrap["bootstrap.py
build_app_state()"]

    subgraph Command ["Command side (writes)"]
        CmdHandler["services/command_handlers.py
CommandHandler.handle()"]:::command
        Commands["domain/commands.py"]:::command
        Aggregates["domain/models.py
Book · Order · OrderItem"]:::command
    end

    BookRepo["services/repos.py
BookRepository"]
    OrderRepo["services/repos.py
OrderRepository"]

    subgraph Persist ["Persistence"]
        ORM["db/models.py
SQLAlchemy ORM models"]:::db
        Session["db/session.py
engine · get_session()
SQLite (data.db)"]:::db
    end

    subgraph Events ["Event-driven notifications"]
        style Events fill:#fffbeb,stroke:#d97706,stroke-width:1px
        Bus["events/bus.py
EventBus.publish()"]
        Disp["events/notifications.py
NotificationDispatcher"]
        Notifs["events/notifications.py
Notification types"]
        Handler["NotificationHandler.dispatch()"]
        Store["events/store.py
NotificationStore.append()"]
    end

    subgraph Query ["Query side (reads)"]
        QH["services/query_handlers.py
QueryHandler.handle()"]:::query
        Queries["domain/queries.py"]:::query
    end

    Client -->|POST / GET| Endpoints
    Endpoints -->|Depends| Deps
    Deps -->|CmdHandlerDep| CmdHandler
    Deps -->|QueryHandlerDep| QH
    Main -->|build_app_state| Bootstrap
    Bootstrap -.->|wire| CmdHandler
    Bootstrap -.->|wire| QH
    Bootstrap -.->|wire| Store

    CmdHandler -->|isinstance dispatch| Commands
    CmdHandler -->|mutate| Aggregates
    CmdHandler -->|save / get| BookRepo
    CmdHandler -->|save / get| OrderRepo
    BookRepo -->|SQLAlchemy Session| ORM
    OrderRepo -->|SQLAlchemy Session| ORM
    ORM -->|bind| Session

    CmdHandler -->|publish| Bus
    Bus -->|on_*| Disp
    Disp -->|build Notification| Notifs
    Notifs -->|dispatch| Handler
    Handler -->|append| Store

    QH --> Queries
    QH -->|get / all| BookRepo
    QH -->|get / all| OrderRepo
    BookRepo -->|to_domain| Aggregates
    OrderRepo -->|to_domain| Aggregates

    Store -.->|SSE stream: GET /api/v1/notifications/stream| Endpoints
```

View the rendered image: [diagrams/control-flow.png](diagrams/control-flow.png)

## Reference material

[Arjan Codes - CQRS YT](https://www.youtube.com/watch?v=Spp-uzXzzdE)
[Arjan Codes - CQRS GH repo](https://github.com/ArjanCodes/examples/tree/main/2026/cqrs)
[G4G Outbox pattern](https://www.geeksforgeeks.org/system-design/outbox-pattern-for-reliable-messaging-system-design/)
[G4G Event-Driven Architecture](https://www.geeksforgeeks.org/system-design/event-driven-architecture-in-an-e-commerce-system/)
[G4G CQRS](https://www.geeksforgeeks.org/system-design/cqrs-command-query-responsibility-segregation/#google_vignette)
[A Practical Introduction to the Event Driven Architecture(GO)](https://dev.to/jimjunior/a-practical-introduction-to-the-event-driven-architecture-dol)
[Real-World Event Driven Architecture](https://streamkap.com/resources-and-guides/event-driven-architecture-examples)
[Event Sourcing with PostgreSQL](https://medium.com/@tobyhede/event-sourcing-with-postgresql-28c5e8f211a2)

[SQLAlchemy patterns](https://tessl.io/registry/tessl-labs/sqlalchemy-best-practices)
