# UWSGI Configs

## Usage

| Index | Server | Command                                  | Make command         |
|-------|--------|------------------------------------------|----------------------|
| 0     | Static | `$ uwsgi --ini configs/uwsgi/static.ini` | `$ make uwsgi-proxy` |
| 1     | Proxy  | `$ uwsgi --ini configs/uwsgi/proxy.ini`  | `$ make uwsgi-static`|

> [!IMPORTANT]
> Modify the config to match your preference.

