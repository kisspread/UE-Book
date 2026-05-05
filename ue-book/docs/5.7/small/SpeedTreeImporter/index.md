# SpeedTree Importer

> An importer for SpeedTree runtime files.

| 属性 | 值 |
|---|---|
| 分类 | Importers |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 是 |
| 模块 | SpeedTreeImporter (Editor) |
| 创建时间 | 2014-05-13 |
| 年龄标签 | 🏛️ 文物(>10年) |
| 作者 | IDV, Inc. |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/SpeedTreeImporter) | |

## 用途

SpeedTree Importer 是 UE5 内置的 SpeedTree 植物资产导入器，负责将 [SpeedTree](https://www.speedtree.com/) 生成的树木运行时文件（`.srt` / `.st` / `.st9`）导入为引擎内的 `UStaticMesh` 资产。

SpeedTree 是业界广泛使用的程序化植被建模工具，由 IDV, Inc. 开发。该 importer 在导入过程中自动完成以下工作：

- **解析 SpeedTree 文件**：支持三个版本的文件格式——SpeedTree 7（`.srt`）、SpeedTree 8（`.st`）和 SpeedTree 9（`.st9`），通过文件头魔数校验确保文件合法性
- **生成网格体**：将 SpeedTree 的几何数据转换为 UE `UStaticMesh`，支持 3D LOD 和 Billboard 两种几何导入方式
- **创建材质**：自动根据 SpeedTree 文件中嵌入的材质信息创建 UE 材质实例（`UMaterialInstanceConstant`），并应用内置的 SpeedTree Master Material 模板
- **导入纹理**：从 SpeedTree 文件引用的纹理路径自动导入贴图（漫反射、法线、遮罩等）
- **风力动画**：集成 SpeedTree 风力系统，通过 `UMaterialExpressionSpeedTree` 表达式在材质中驱动顶点风力动画
- **物理碰撞**：可选择导入 SpeedTree 定义的碰撞几何（球体和胶囊体）
- **Reimport 支持**：已导入的资产可右键重新导入，保留原有导入选项

插件在 `Content/SpeedTree9/` 目录下预置了 SpeedTree 9 的 Master Material 模板（`SpeedTreeMaster`、`SpeedTreeBillboardMaster` 等），导入时会基于这些模板创建材质实例。

## 使用场景

- 你使用 SpeedTree 建模了树木/植被，需要导入到 UE5 项目 → 直接拖放 `.srt`/`.st`/`.st9` 文件到 Content Browser
- 你购买了 SpeedTree 商城的植被资产（如 `.st` 格式），需要批量导入 → 使用 Import 功能
- SpeedTree 源文件更新后需要同步到引擎 → 在已导入的 StaticMesh 上右键 → Reimport
- 你需要为植被创建带动画的材质（风吹树叶摇摆）→ 启用 Import 选项中的 Wind 材质功能

## 蓝图用法

该插件没有暴露任何 `BlueprintCallable` 或 `BlueprintReadWrite` 接口。它是一个纯编辑器导入工具，不提供运行时蓝图 API。所有操作通过编辑器 UI 完成。

## C++ 用法

该插件的所有模块依赖均为 `PrivateDependencyModuleNames`，没有对外暴露公共 C++ API（`PublicDependencyModuleNames` 为空）。这意味着其他模块无法直接引用 SpeedTreeImporter 的类。

插件的核心类结构：

### 核心类

| 类 | 基类 | 职责 |
|---|---|---|
| `USpeedTreeImportFactory` | `UFactory` | 主导入工厂，注册 `.srt`/`.st`/`.st9` 格式，执行实际导入逻辑 |
| `UReimportSpeedTreeFactory` | `USpeedTreeImportFactory` + `FReimportHandler` | 重新导入处理器，支持右键 Reimport |
| `USpeedTreeImportData` | `UAssetImportData` | 存储导入选项（缩放、材质开关等），持久化到配置文件 |
| `FSpeedTreeImportDataDetails` | `IDetailCustomization` | 导入选项对话框的 UI 定制，根据 SpeedTree 版本动态显示/隐藏选项 |

### 导入选项

通过导入时弹出的选项对话框（`SSpeedTreeImportOptions`）可以配置以下参数：

**Mesh 选项**

| 选项 | 说明 | 适用版本 |
|---|---|---|
| Tree Scale | 树木缩放比例，默认 30.48（英尺转厘米） | v7 |
| Geometry | 导入几何类型：3D LODs / Billboards / Both | v7 |
| LOD Setup | LOD 方式：Painted Foliage / Individual Actors | v8 |
| Include Collision | 是否导入碰撞几何 | v8 |

**Materials 选项**

| 选项 | 说明 | 适用版本 |
|---|---|---|
| Create Materials | 是否自动创建材质 | v8 |
| Include Normal Maps | 导入法线贴图 | 全版本 |
| Include Detail Maps | 导入细节贴图 | 全版本 |
| Include Specular Maps | 导入高光贴图 | 全版本 |
| Include Branch Seam Smoothing | 分支接缝平滑 | 全版本 |
| Include SpeedTree AO | SpeedTree 环境光遮蔽 | 全版本 |
| Include Random Color Variation | 随机颜色变化 | 全版本 |
| Include Subsurface | 次表面散射 | v8 |
| Include Vertex Processing | 顶点处理（含 Wind 和 Smooth LOD 子选项） | v8 |
| Include Wind | 风力动画 | v8（需开启 Vertex Processing） |
| Include Smooth LOD | 平滑 LOD 过渡 | v8（需开启 Vertex Processing） |

### 文件格式识别

导入器通过读取文件头部字节来验证文件合法性：

- `.srt` 文件：前 4 字节为 `"SRT "`（ASCII）
- `.st` 文件：前 12 字节为 `"SpeedTree___"`
- `.st9` 文件：前 16 字节为 `"SpeedTree9______"`

### 材质模板

导入器使用插件 `Content/SpeedTree9/` 目录下的材质资产作为模板：

| 模板资产 | 用途 |
|---|---|
| `SpeedTreeMaster` | 3D 网格体的主材质模板 |
| `SpeedTreeBillboardMaster` | Billboard 的材质模板 |
| `SpeedTreeWindMotion` | 风力运动材质函数 |
| `SpeedTreeWind` | 风力材质函数 |
| `SpeedTreeBranchMotion` | 树枝运动材质函数 |
| `SpeedTreeCameraFacing` | 面向相机材质函数 |
| `SpeedTreeBillboard` | Billboard 材质函数 |
| `UnpackInteger3` / `UnpackDirection` / `Empty` / `EmptyNormal` | 辅助工具材质函数 |

## Demo 示例

该插件不提供可编程 API，使用方式完全通过编辑器 UI 操作：

1. 在 SpeedTree 桌面应用中创建或打开树木模型
2. 导出为 `.st`（v8）或 `.st9`（v9）格式的运行时文件
3. 在 UE5 Content Browser 中点击 **Import**，或直接将文件拖入 Content Browser
4. 在弹出的导入选项对话框中配置几何类型、材质选项等
5. 点击 **Import** 完成导入
6. 导入后会在 Content Browser 中生成 `UStaticMesh` 资产及相关材质/纹理
7. 如需更新，在已导入的 StaticMesh 上右键 → **Reimport**

## 模块依赖

所有依赖均为私有（`PrivateDependencyModuleNames`），不影响使用者的模块配置：

| 模块 | 用途 |
|---|---|
| `Core` | 基础核心库 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心（StaticMesh、Texture 等） |
| `Slate` / `SlateCore` | 导入选项 UI 框架 |
| `InputCore` | 输入处理 |
| `EditorFramework` | 编辑器框架（AssetImportData） |
| `UnrealEd` | 编辑器核心（Factory、ReimportHandler） |
| `MainFrame` | 主窗口交互 |
| `MeshDescription` | 网格体描述数据 |
| `StaticMeshDescription` | 静态网格体描述 |
| `SpeedTree`（第三方） | SpeedTree 运行时库（`SpeedTreeWind` 等） |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-07-14 | `8c4cad9` | Changed all WITH_EDITORONLY_DATA properties in StaticMesh to have accessors | 引擎层重构，StaticMesh 内部访问器变更，SpeedTreeImporter 作为依赖方被同步更新 |
| 2025-06-26 | `a2e7518` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files | 代码质量优化，减少编译时间的宏改进 |
| 2025-05-23 | `8f4fd6f` | Removed use of the world master in the speed tree importer plugin | 功能性更新：移除了对 world master 的依赖，简化导入流程 |

### 维护评价

- **年龄**：2014 年创建，已超过 11 年，是 UE 最老的插件之一
- **最近更新**：2025 年 7 月仍有更新，但最近三次 commit 均为引擎层适配（编译修复、代码质量优化），仅 2025-05-23 的提交有实质性功能变更
- **维护状态**：**维护中** — 持续跟随引擎版本迭代，但核心功能长期稳定，无需频繁更新
- **已知限制**：
  - 所有依赖均为私有，无法从 C++ 直接调用其功能
  - 需要 SpeedTree 第三方库支持（`WITH_SPEEDTREE` 编译宏），无 SpeedTree SDK 时功能受限
  - 没有 Blueprint API，无法通过蓝图自动化导入流程
  - v7 格式（`.srt`）的部分选项与 v8/v9 不同
- **推荐程度**：✅ **推荐使用** — 这是官方维护的 SpeedTree 导入方案，功能完整且稳定。如果你使用 SpeedTree 工具制作植被，这是唯一的官方导入路径。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/SpeedTreeImporter)
- [SpeedTree 官方网站](https://www.speedtree.com/)
- [UE5 官方文档 - SpeedTree](https://docs.unrealengine.com/5.6/en-US/speedtree-in-unreal-engine/)
