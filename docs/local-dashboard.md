# Local dashboard setup

Run the Vigilattice backend and frontend in separate Terminal windows.

## Start the backend

```bash
cd ~/Downloads/Vigilattice
make api
```

The API runs at `http://localhost:8000`.

## Start the frontend

```bash
cd ~/Downloads/Vigilattice
make web
```

Open the dashboard at `http://localhost:5173`.

The benchmark controls remain disabled until both services are running.
