# Mydea Community

[English](./README.md) | [中文](./README-cn.md)

Mydea Community 是 Mydea 原生资源的内容、协作与审核仓库。

## 贡献资源

1. Fork 本仓库。
2. 将导出的文件上传到对应集合目录：`collections/<collection>/<language>/`（页面、区块、列表）或 `themes/`。
3. 创建 Pull Request。

文件必须保留 Mydea 导出的原始 JSON 格式。不要手工编辑 Registry、digest、PR 编号或 Featured 信息。

CI 会检查 JSON、文件位置、文件名、资源 Schema，以及 Page/Section 对 Community List 的引用。合并到 `main` 后，发布工作流会重新校验并生成 `registry` 分支。

## 资源下载

消费者读取 `registry/registry.json`，再用 `repository` 和条目的 `path` 从 `main` 下载资源。Registry 不做版本管理，始终指向最新数据。条目的 `digest` 是变更令牌：与本地副本比对即可判断哪些资源需要重新下载。

## 本地校验与构建

```sh
python3 .community/scripts/validate.py
python3 .community/scripts/build_registry.py --repository OWNER/mydea-community
```

## 示例

`collections/cannes/en/cannes-prizes.page.json` 使用同目录的 `cannes-2026.list.json`。Registry 入口是根目录下的 `registry.json`，其 `catalogs.pages`（及 `sections`/`lists`）列出每个拥有对应 Catalog 的语言目录，例如 `en/pages.json`；`catalogs.themes` 始终为 `["."]`，对应根目录下的 `themes.json`。Catalog 条目的 `path` 本身已带有 `<language>/<filename>` 形式。
