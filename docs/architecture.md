```mermaid
graph TD
    A[Frontend] -->|HTTP| B[Auth Service]
    A -->|HTTP| C[Forms Service]
    B -->|gRPC| D[DB Auth]
    C -->|gRPC| E[DB Forms]
```м