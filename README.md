# clickup-mcp

Servidor MCP para ClickUp, escrito em Python com [FastMCP](https://github.com/jlowin/fastmcp).

Substitui o `@nazruden/clickup-server` (Node.js) com **paridade total de features** e adiciona leitura completa do corpo/description das tasks — funcionalidade ausente no servidor original.

## Funcionalidades

- **35 tools** cobrindo toda a hierarquia do ClickUp: Workspaces → Spaces → Folders → Lists → Tasks → Comments → Views → Custom Fields → Docs
- `get_task` retorna `description`, `text_content` e `markdown_description` — o diferencial principal
- Suporte a Docs via API v3 (criar, listar páginas, ler e editar conteúdo em Markdown)
- Async puro com `httpx`, sem dependências pesadas

## Instalação

```bash
git clone https://github.com/jlpitta/clickup-mcp.git
cd clickup-mcp
pip install -r requirements.txt
```

## Configuração MCP

Adicione ao seu `mcp.json` (Kiro, Claude Code ou qualquer cliente MCP):

```json
{
  "mcpServers": {
    "clickup": {
      "command": "python3",
      "args": ["/caminho/para/clickup-mcp/server.py"],
      "env": {
        "CLICKUP_API_TOKEN": "pk_..."
      }
    }
  }
}
```

> O token **não** é armazenado no repositório. Configure apenas localmente.
>
> Para obter o token: **ClickUp → Settings → Apps → API Token**

## Tools disponíveis

### Workspaces

| Tool | Descrição |
|------|-----------|
| `get_teams` | Lista todos os workspaces acessíveis ao usuário autenticado |

### Spaces

| Tool | Parâmetros principais | Descrição |
|------|-----------------------|-----------|
| `get_spaces` | `team_id` | Lista todos os spaces de um workspace |
| `get_space` | `space_id` | Detalhes de um space específico |
| `create_space` | `team_id`, `name` | Cria um novo space |
| `update_space` | `space_id`, `name` | Renomeia um space |
| `delete_space` | `space_id` | Remove um space |

### Folders

| Tool | Parâmetros principais | Descrição |
|------|-----------------------|-----------|
| `get_folders` | `space_id` | Lista pastas de um space |
| `get_folder` | `folder_id` | Detalhes de uma pasta |
| `create_folder` | `space_id`, `name` | Cria uma pasta |
| `update_folder` | `folder_id`, `name` | Renomeia uma pasta |
| `delete_folder` | `folder_id` | Remove uma pasta |

### Lists

| Tool | Parâmetros principais | Descrição |
|------|-----------------------|-----------|
| `get_lists` | `folder_id` | Lists dentro de uma pasta |
| `get_folderless_lists` | `space_id` | Lists diretamente sob um space (sem pasta) |
| `create_list` | `parent_id`, `parent_type`, `name` | Cria uma list em pasta (`folder`) ou space (`space`) |

### Tasks

| Tool | Parâmetros principais | Descrição |
|------|-----------------------|-----------|
| `get_tasks` | `list_id` | Tasks de uma lista (resumo: nome, status, assignees, prioridade) |
| `get_task` | `task_id` | **Detalhes completos**, incluindo `description`, `text_content`, `markdown_description`, custom fields e tags |
| `create_task` | `list_id`, `name` | Cria uma task com descrição, status, prioridade, assignees, due date e tags opcionais |
| `update_task` | `task_id` | Atualiza qualquer campo de uma task existente |

### Comments

| Tool | Parâmetros principais | Descrição |
|------|-----------------------|-----------|
| `get_comments` | `task_id` | Lista todos os comentários de uma task |
| `add_comment` | `task_id`, `text` | Adiciona um comentário a uma task |

### Views

| Tool | Parâmetros principais | Descrição |
|------|-----------------------|-----------|
| `get_views` | `parent_id`, `parent_type` | Views de um team/space/folder/list |
| `get_view` | `view_id` | Detalhes de uma view |
| `get_view_tasks` | `view_id` | Tasks de uma view |
| `create_view` | `parent_id`, `parent_type`, `name`, `view_type` | Cria uma view (`list`, `board`, `calendar`, `gantt`) |
| `delete_view` | `view_id` | Remove uma view |
| `create_board` | `space_id`, `name` | Atalho para criar uma board view em um space |

### Custom Fields

| Tool | Parâmetros principais | Descrição |
|------|-----------------------|-----------|
| `get_custom_fields` | `list_id` | Lista os custom fields de uma lista |
| `set_custom_field` | `task_id`, `field_id`, `value` | Define o valor de um custom field em uma task |
| `remove_custom_field` | `task_id`, `field_id` | Remove o valor de um custom field |

### Docs (API v3)

| Tool | Parâmetros principais | Descrição |
|------|-----------------------|-----------|
| `search_docs` | `team_id`, `query` | Busca docs em um workspace |
| `get_doc_pages` | `workspace_id`, `doc_id` | Lista as páginas de um doc |
| `get_doc_page_content` | `workspace_id`, `doc_id`, `page_id` | Conteúdo de uma página em Markdown |
| `create_doc` | `workspace_id`, `name` | Cria um novo doc (suporta parent: space/folder/list/workspace) |
| `create_doc_page` | `workspace_id`, `doc_id`, `name` | Cria uma página em um doc |
| `edit_doc_page` | `workspace_id`, `doc_id`, `page_id`, `content` | Substitui o conteúdo de uma página |

## Dependências

```
mcp[cli]>=1.0.0
httpx>=0.27.0
```
