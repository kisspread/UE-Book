# PROJ 模块（External）

> 第三方外部模块，封装 PROJ 坐标转换库的跨平台链接配置。

## 模块信息

| 属性 | 值 |
|---|---|
| 类型 | External |
| 路径 | `Source/ThirdParty/Proj.Build.cs` |

## 说明

此模块不包含 UE 代码，仅负责配置 [PROJ](https://proj.org/) 库的跨平台链接。PROJ 是一个通用的坐标转换库，支持数千种 CRS 之间的转换。

**Build.cs 配置要点：**
- 通过 vcpkg-installed 目录管理预编译库
- 支持平台：Win64（x64 + ARM64）、Mac（x64+ARM64 Universal）、iOS（ARM64）、Linux（x64）、Android（ARM64 + x64）
- 启用异常处理（`bEnableExceptions = true`）
- 同时打包 SQLite3（PROJ 依赖其内部数据库）

**PROJ 数据文件：**
- 存放在 `Resources/PROJ/` 目录下
- 包含 `proj.db`（CRS 定义数据库）和其他投影数据文件
- 在 RuntimeDependencies 中声明为 UFS 资源
- 编辑器模式直接读取文件系统，打包后通过 UFS（Pak）读取

## 使用者无需直接依赖此模块

`GeoReferencing` 模块已私有依赖 `PROJ`，使用者只需依赖 `GeoReferencing` 即可。
