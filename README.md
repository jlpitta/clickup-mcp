# clickup-mcp

MCP server para ClickUp com suporte a `get_task` (inclui description/body).

## Tools disponíveis

| Tool | Descrição |
|------|-----------|
| `get_task` | Detalhes completos de uma task (com description) |
| `get_tasks_in_list` | Tasks de uma lista |
| `create_task` | Criar task |
| `update_task` | Atualizar task |
| `get_comments` | Comentários de uma task |
| `add_comment` | Adicionar comentário |

## Setup

```bash
git clone https://github.com/jlpitta/clickup-mcp.git ~/.local/share/clickup-mcp
cd ~/.local/share/clickup-mcp
pip install -r requirements.txt
```

## Configuração MCP (Kiro / Claude)

```json
{
  "clickup": {
    "command": "python3",
    "args": ["/home/SEU_USER/.local/share/clickup-mcp/server.py"],
    "env": {
      "CLICKUP_API_TOKEN": "pk_...",
      "CLICKUP_TEAM_ID": "90132925864"
    }
  }
}
```

## Token

O token **NÃO** é armazenado no repositório. Configure apenas no `mcp.json` local de cada máquina.

Obter em: ClickUp → Settings → Apps → API Token
