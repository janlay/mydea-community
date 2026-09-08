# Mydea Community

[English](./README.md) | [中文](./README-cn.md)

Mydea Community 是 Mydea 原生资源的内容、协作与审核仓库。

## 贡献资源

1. Fork 本仓库。
2. 将导出的文件上传到对应集合目录：`<category>/<collection>/<language>/`（页面、区块、列表）或 `themes/`。
3. 创建 Pull Request。

文件必须保留 Mydea 导出的原始 JSON 格式。不要手工编辑 Registry、digest、PR 编号或 Featured 信息。

提交 PR 前请先阅读 [CONTRIBUTING.md](./CONTRIBUTING.md)，其中写明了贡献条款，包括作者身份如何认定，以及贡献者保留哪些权利。

CI 会检查 JSON、文件位置、文件名、资源 Schema，以及 Page/Section 对 Community List 的引用。合并到 `main` 后，发布工作流会重新校验并生成 `registry` 分支。

## 资源下载

消费者读取 `registry/registry.json`，再用 `repository` 和条目的 `path` 从 `main` 下载资源。Registry 不做版本管理，始终指向最新数据。条目的 `digest` 是变更令牌：与本地副本比对即可判断哪些资源需要重新下载。

## 本地校验与构建

```sh
python3 .community/scripts/validate.py
python3 .community/scripts/build_registry.py --repository janlay/mydea-community
```

## 示例

`awards/cannes/en/cannes-10-years.page.json` 使用同目录的 `cannes-2026.list.json`。Registry 入口是根目录下的 `registry.json`，其 `catalogs.pages`（及 `sections`/`lists`）列出每个拥有对应 Catalog 的语言目录，例如 `en/pages.json`；`catalogs.themes` 始终为 `["."]`，对应根目录下的 `themes.json`。Catalog 条目的 `path` 本身已带有 `<language>/<filename>` 形式。

## 许可协议

代码部分，即 `.community/scripts/` 下的脚本和 `.github/` 下的工作流，采用 [MIT 协议](./LICENSE)。

社区资源部分，即所有 Page、Section、List、Theme 文档以及 `.localized.json` 文件，采用 [CC BY-NC-SA 4.0](./LICENSE-CONTENT)：需保留署名，不得用于商业用途，衍生作品须以相同协议发布。转载时请同时署名原贡献者和本仓库。

贡献者保留自己贡献内容的著作权，并对其保留不受限制的使用权，详见 [CONTRIBUTING.md](./CONTRIBUTING.md)。
