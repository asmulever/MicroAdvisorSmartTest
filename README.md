## Dev (VS Code Dev Container)
1) Copiar `.env.example` a `.env`
2) VS Code -> "Reopen in Container"
3) Abrir: http://localhost:8000/health

## Publish (GitHub)
Push a `main` => se publica imagen en GHCR.
Luego desplegás esa imagen donde quieras (VPS, Render, Fly, Railway, etc.)