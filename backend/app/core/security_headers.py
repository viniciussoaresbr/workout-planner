"""Cabeçalhos HTTP de segurança adicionados a todas as respostas da API."""

from starlette.types import ASGIApp, Message, Receive, Scope, Send

# A API só devolve JSON e arquivos para download: nada nela deve ser executado, embutido em
# frames ou ter o tipo adivinhado pelo navegador.
_BASE_HEADERS = {
    "x-content-type-options": "nosniff",
    "x-frame-options": "DENY",
    "referrer-policy": "no-referrer",
    "cross-origin-opener-policy": "same-origin",
}
_API_CSP = "default-src 'none'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'"
# Só faz efeito quando a resposta chega por HTTPS; o navegador passa a recusar HTTP por 2 anos.
_HSTS = "max-age=63072000; includeSubDomains"


class SecurityHeadersMiddleware:
    """Adiciona os cabeçalhos de segurança sem sobrescrever os que a rota já definiu.

    `csp_exempt_paths` recebe as páginas de documentação (Swagger/ReDoc), que carregam
    scripts de CDN e quebrariam com a CSP restritiva. Elas só existem fora de produção.
    """

    def __init__(
        self, app: ASGIApp, *, hsts: bool, csp_exempt_paths: frozenset[str] = frozenset()
    ) -> None:
        self.app = app
        self.hsts = hsts
        self.csp_exempt_paths = csp_exempt_paths

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        extra = dict(_BASE_HEADERS)
        if scope["path"] not in self.csp_exempt_paths:
            extra["content-security-policy"] = _API_CSP
        if self.hsts:
            extra["strict-transport-security"] = _HSTS

        async def send_with_headers(message: Message) -> None:
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))
                present = {name.lower() for name, _ in headers}
                headers.extend(
                    (name.encode(), value.encode())
                    for name, value in extra.items()
                    if name.encode() not in present
                )
                message["headers"] = headers
            await send(message)

        await self.app(scope, receive, send_with_headers)
