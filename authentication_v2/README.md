# The `password` flow

- user types `username` and `password` in the frontend
- the frontend sends the `username` and `password` to a specific URL in our API (declared as `tokenUrl=token`).
- the API checks the `username` and `passwrd` and responds with a `token`.
- the frontend stores that token temporarily somewhere
- the user clicks elsewhere in the frontend
- the frontend sends a header `Authorization` with a value of **`Bearer` plus the `token`**.

```shell
curl -X 'GET' \
  'http://127.0.0.1:8000/items/' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer SOMETOKENVALUE'
```

When the frontend sends the `Authorization` header we can return the user.

```shell
curl -X 'GET' \                                                                                               master@singularity
  'http://127.0.0.1:8000/users/me' \
  -H 'accept: application/json' \
-H 'Authorization: Bearer SOMETOKENVALUE'

# {"username":"SOMETOKENVALUE-Fakedecoded","email":"ioannis@example.com","full_name":"Ioannis Petrousov","disabled":null}%
````
