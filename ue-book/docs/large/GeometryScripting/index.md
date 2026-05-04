# Geometry Script

> Geometry Script provides a library of functions for creating and editing Meshes in Blueprints and Python

| 属性 | 值 |
|---|---|
| 分类 | Geometry |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、材质模板） |
| 模块 | `GeometryScriptingCore` (Runtime), `GeometryScriptingEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2021-09-12 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/GeometryScripting) | |

## 用途

Geometry Scripting 是 UE5 的程序化几何操作插件，通过蓝图和 Python 暴露完整的网格创建、查询、编辑与处理能力。它将 GeometryCore/DynamicMesh 底层算法封装为蓝图函数库，使非程序员也能进行复杂的程序化几何操作。

插件由两个模块组成：

- **GeometryScriptingCore**（Runtime）— 核心蓝图函数库，涵盖网格图元创建、布尔运算、UV 操作、网格修复、简化、变形、碰撞生成等全部运行时功能。打包后仍可使用，适合游戏内程序化生成。
- **GeometryScriptingEditor**（Editor）— 编辑器专用扩展，补充 Core 模块在编辑器环境下才可执行的功能：资产创建导出（StaticMesh/SkeletalMesh/Texture2D/Volume）、纹理通道打包（Channel Pack）、OpenSubdiv 细分曲面、Undo/Redo 事务支持，以及程序化网格生成 Actor（`AGeneratedDynamicMeshActor`）。

核心价值：
- **运行时可用**：打包后仍可使用，适合游戏内程序化生成
- **蓝图友好**：所有操作都是 `BlueprintCallable`/`BlueprintPure`，支持链式调用
- **基于 UDynamicMesh**：轻量级运行时网格，无需 StaticMesh 资产
- **功能全面**：从基础查询到布尔运算、UV 展开、网格修复、资产导出等

## 跨模块使用场景

| 场景 | Core 模块 | Editor 模块 |
|---|---|---|
| 运行时程序化网格生成 | ✅ 图元创建 + 布尔运算 + 变形 | ❌ 不可用 |
| 编辑器中程序化建模并导出资产 | ✅ 构建 DynamicMesh | ✅ `CreateNewStaticMeshAssetFromMesh` |
| 纹理通道合并（Roughness+Metallic+AO） | ❌ | ✅ `Channel Pack` |
| 模型细分（Catmull-Clark / Loop） | ❌ | ✅ `Apply PolyGroup Catmull Clark SubD` |
| 蓝图中修改网格支持 Undo | ❌ | ✅ `BeginTrackedMeshChange` + `EmitTrackedMeshChange` |
| 编辑器程序化网格 Actor | ❌ | ✅ `AGeneratedDynamicMeshActor` |
| 网格修复流水线 | ✅ WeldMeshEdges / FillAllMeshHoles | — |
| 程序化 UV 展开与打包 | ✅ RecomputeMeshUVs / RepackMeshUVs | — |

## 模块列表

| 模块 | 类型 | 说明 | 文档 |
|---|---|---|---|
| `GeometryScriptingCore` | Runtime | 核心蓝图函数库：网格创建、编辑、查询、布尔运算、UV、修复、简化等 | [GeometryScriptingCore.md](GeometryScriptingCore.md) |
| `GeometryScriptingEditor` | Editor | 编辑器扩展：资产创建导出、纹理 Channel Pack、OpenSubdiv 细分、Undo 支持、程序化生成 Actor | [GeometryScriptingEditor.md](GeometryScriptingEditor.md) |

## 维护状态

### 近期更新

| 日期 | Commit | 说明 |
|---|---|---|
| 2025-09-10 | `9046d13` | 移动 DynamicMesh MIKT 支持，修复网格覆盖层中未设置元素（法线、UV）的处理 |
| 2025-09-03 | `35e7aa5` | 修复新定向盒方法 — 对盒轴应用未缩放变换 + 修复 OBB→ABB 转换的显示名 |
| 2025-09-03 | `9c4ba7b` | 添加定向盒（Oriented Box）形状函数到 Geometry Script |

### 维护评价

- **活跃维护**：最近 6 个月内持续有功能性更新（Oriented Box、MIKT 支持等）
- **创建时间**：2021 年 9 月（从 Experimental 迁移到 Runtime）
- **更新频率**：频繁，持续添加新功能
- **稳定性**：已从实验性毕业为正式 Runtime 模块
- **推荐程度**：✅ 强烈推荐 — UE5 程序化几何操作的标准方案，蓝图和 C++ 均可使用，运行时可用

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/GeometryScripting)
- [官方文档]()（.uplugin 中未提供 DocsURL）
