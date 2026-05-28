# GeometryMode

> Geometry and BSP editing（照抄）

| 属性 | 值 |
|---|---|
| 中文名 | 几何体模式 |
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `GeometryMode` (Editor), `BspMode` (Editor), `TextureAlignMode` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2019-10-28 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/GeometryMode) | |

## 用途

该插件将 BSP（二元空间分割）几何体编辑器模式从引擎核心代码迁移到了独立插件中，方便在某些项目配置下禁用。BSP 几何体是 UE 中传统的关卡原型设计工具，允许设计师直接在编辑器中通过拉伸、切割、合并等操作快速搭建关卡白盒。

插件提供三大功能模块：

- **几何体编辑**：基础的几何体/多边形编辑操作（拉伸、内插、切割等）
- **BSP 模式**：BSP 画刷的创建、操作与管理，包括实体/半透明画刷的编辑
- **纹理对齐**：对 BSP 表面进行纹理平移、旋转、缩放等对齐操作

## 模块一览

| 模块 | 类型 | 文档 | 说明 |
|---|---|---|---|
| `GeometryMode` | Editor | [GeometryMode.md](GeometryMode.md) | 核心几何体编辑器模式，提供多边形/顶点/边编辑工具（拉伸、内插、切割、翻转等） |
| `BspMode` | Editor | [BspMode.md](BspMode.md) | BSP 画刷编辑器模式，提供画刷创建、CSG 操作（加、减、交）、画刷管理与属性面板 |
| `TextureAlignMode` | Editor | [TextureAlignMode.md](TextureAlignMode.md) | BSP 表面纹理对齐模式，提供纹理平移、旋转、缩放、对齐及 Panini 投影映射工具 |

## 使用场景

- 你在用 BSP 画刷搭建关卡原型/白盒 → 用 **BspMode**
- 你需要对 BSP 或几何体进行精细的多边形编辑（切割、内插、翻转法线等）→ 用 **GeometryMode**
- 你需要调整 BSP 表面上的纹理位置和对齐方式 → 用 **TextureAlignMode**

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `fbd199ea` | [Backout] - CL53903539 | 回退某次变更 |
| 2026-05-14 | `5c94be5d` | Global snapping toggle in toolbar, and (red) indicator when one or more snapping options are enabled | 工具栏新增全局吸附开关，启用时显示红色指示器 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移到 UE_LOGF |
| 2026-02-25 | `12a309dc` | Remove as many PVS suppressions as possible that are no longer needed | 清理不再需要的 PVS 静态分析抑制 |
| 2026-02-03 | `61433296` | Rename FViewMatrices members to follow the `<Source>To<Target>` pattern for transforms, to reduce ambi | 重命名 FViewMatrices 成员以遵循统一命名规范 |

### 维护评价

该插件自 2019 年从引擎代码迁出后持续维护，2026 年仍有功能性更新（如全局吸附开关）和代码质量改进。作为 BSP 编辑的核心基础设施，虽然 BSP 关卡设计在现代项目中已逐渐被静态网格体取代，但插件仍保持活跃维护。**推荐在需要 BSP 编辑功能时使用**，注意该插件默认启用；如果你的项目不使用 BSP 画刷，可以安全地禁用以减少编辑器复杂度。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/GeometryMode)
- [子模块文档 - GeometryMode](GeometryMode.md)
- [子模块文档 - BspMode](BspMode.md)
- [子模块文档 - TextureAlignMode](TextureAlignMode.md)