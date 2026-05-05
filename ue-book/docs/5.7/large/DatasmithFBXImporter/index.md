# Datasmith FBX Importer

> Adds support for importing content from DeltaGen and VRED into Unreal Engine

| 属性 | 值 |
|---|---|
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DatasmithFBXTranslator` (Editor), `DatasmithVREDTranslator` (Editor), `DatasmithDeltaGenTranslator` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 🏛️ 文物（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/DatasmithFBXImporter) | |

## 用途

本插件是 Datasmith 导入管线的专用扩展，为两款汽车行业主流 3D 可视化软件——**Autodesk VRED** 和 **DeltaGen (RTT AG)**——提供原生 FBX 场景导入支持。

普通的 FBX Importer 只处理几何体、材质和基本动画；而本插件理解 VRED 和 DeltaGen 的专有工作流，能够：

- **解析辅助文件**：VRED 的 `.mats`（材质）、`.var`（变体）、`.lights`（灯光）、`.clips`（动画剪辑）；DeltaGen 的 `.var`、`.pos`（状态）、`.tml`（时间线动画）
- **保留产品可视化特性**：变体切换（Variant Sets）、Switch/Toggle 节点、动画剪辑组合
- **智能场景优化**：去重网格体和材质、简化节点层级、拆分灯光/摄像机节点以适配 UE 坐标系
- **材质精准还原**：通过参考材质系统（Reference Material Selector）将 VRED/DeltaGen 材质映射为 UE 材质实例

**为什么存在？** VRED 和 DeltaGen 都使用 FBX 作为导出格式，但 FBX 文件中嵌入了大量专有元数据。普通 FBX 导入器无法识别这些信息，导致变体丢失、动画错乱、材质退化。本插件通过读取 FBX 头信息识别来源应用，然后用专有的解析逻辑提取完整场景语义。

## 使用场景

- 你在用 **Autodesk VRED** 做汽车配置器/展厅渲染，需要将完整场景（含变体、动画剪辑、灯光配置）导入 UE5 → 启用本插件
- 你在用 **DeltaGen** 做汽车设计评审，需要导入包含 POV 状态、时间线动画、变体切换的 FBX 场景 → 启用本插件
- 你只是导入普通 FBX 模型（从 3ds Max / Maya / Blender 导出）→ **不需要**本插件，使用内置 FBX Importer 即可
- 你通过 Python 脚本自动化 VRED/DeltaGen 场景导入流水线 → 本插件提供 Python API 支持

## 蓝图用法

本插件本身不暴露 BlueprintCallable 节点。它通过 Datasmith 的 Translator 机制注册，当用户在编辑器中导入 FBX 文件时自动生效。

但导入的场景数据（变体、动画等）可通过 Datasmith Content 插件的蓝图接口访问：

### 导入选项类（蓝图可配置）

| 类 | 说明 | 所在模块 |
|---|---|---|
| `UDatasmithFBXImportOptions` | 基础 FBX 导入选项，包含纹理搜索路径 `TextureDirs` | `DatasmithFBXTranslator` |
| `UDatasmithVREDImportOptions` | VRED 专用选项，继承自 FBX 基础选项 | `DatasmithVREDTranslator` |
| `UDatasmithDeltaGenImportOptions` | DeltaGen 专用选项，继承自 FBX 基础选项 | `DatasmithDeltaGenTranslator` |

### VRED 导入选项

| 属性 | 类型 | 说明 |
|---|---|---|
| `bImportMats` | `bool` | 是否导入 `.mats` 材质文件以获得更精确的材质还原 |
| `MatsPath` | `FFilePath` | `.mats` 文件路径（默认自动搜索同目录同名文件） |
| `bImportVar` | `bool` | 是否导入 `.var` 变体文件 |
| `bCleanVar` | `bool` | 清理空变体和无效选项 |
| `VarPath` | `FFilePath` | `.var` 文件路径 |
| `bImportLightInfo` | `bool` | 是否导入 `.lights` 灯光文件 |
| `LightInfoPath` | `FFilePath` | `.lights` 文件路径 |
| `bImportClipInfo` | `bool` | 是否导入 `.clips` 动画剪辑文件 |
| `ClipInfoPath` | `FFilePath` | `.clips` 文件路径 |

### DeltaGen 导入选项

| 属性 | 类型 | 说明 |
|---|---|---|
| `bRemoveInvisibleNodes` | `bool` | 移除 FBX 中标记为不可见的节点（变体切换节点除外） |
| `bSimplifyNodeHierarchy` | `bool` | 折叠恒等变换、无网格、无动画/变体的空节点 |
| `bImportVar` | `bool` | 是否导入 `.var` 变体文件 |
| `VarPath` | `FFilePath` | `.var` 文件路径 |
| `bImportPos` | `bool` | 是否导入 `.pos` 状态文件 |
| `PosPath` | `FFilePath` | `.pos` 文件路径 |
| `bImportTml` | `bool` | 是否导入 `.tml` 时间线动画文件 |
| `TmlPath` | `FFilePath` | `.tml` 文件路径 |
| `ShadowTextureMode` | `EShadowTextureMode` | 阴影纹理处理方式：忽略 / AO / 乘法 / 两者兼有 |

## C++ 用法

本插件是纯 Editor 模块，不设计为被外部模块直接链接。其公共 API 主要面向 Datasmith Translator 扩展开发。

### 核心类层次

```
IDatasmithTranslator (DatasmithTranslator 模块)
├── FDatasmithVREDTranslator    ← 注册为 "VRED" 翻译器
└── FDatasmithDeltaGenTranslator ← 注册为 "Deltagen" 翻译器

FDatasmithFBXImporter (基类)
├── FDatasmithVREDImporter
└── FDatasmithDeltaGenImporter

FDatasmithFBXSceneProcessor (基类)
├── FDatasmithVREDSceneProcessor
└── FDatasmithDeltaGenSceneProcessor
```

### 头文件引入

```cpp
#include "DatasmithFBXScene.h"          // 中间场景表示
#include "DatasmithFBXImporter.h"       // FBX 导入器基类
#include "DatasmithFBXSceneProcessor.h" // 场景处理器基类
#include "DatasmithFBXFileImporter.h"   // FBX 文件解析
#include "DatasmithFBXHashUtils.h"      // MD5 哈希工具
#include "DatasmithFBXImportOptions.h"  // 导入选项基类
```

### 中间场景数据结构

插件使用 `FDatasmithFBXScene` 作为 FBX 文件与 Datasmith 元素之间的中间表示：

```cpp
// FBX 场景的中间表示
struct FDatasmithFBXScene
{
    TSharedPtr<FDatasmithFBXSceneNode> RootNode;      // 场景根节点
    TArray<TSharedPtr<FDatasmithFBXSceneMaterial>> Materials; // 材质列表
    TArray<FDatasmithFBXSceneAnimNode> AnimNodes;     // 动画节点
    TArray<FName> SwitchObjects;      // 切换对象
    TArray<FName> ToggleObjects;      // 开关对象
    TArray<FName> AnimatedObjects;    // 动画对象
    TArray<FName> TransformVariantObjects; // 变换变体对象
    float TagTime = FLT_MAX;          // VRED DSID 标记时间
    float BaseTime = 24.0f;           // 原生帧率
    float PlaybackSpeed = 24.0f;      // 播放速度
    double ScaleFactor = 1.0f;        // 单位缩放因子
};
```

### 节点类型标志

```cpp
enum class ENodeType : uint32
{
    Node = 0,
    Switch = 1,      // 变体切换节点
    SharedNode = 2,  // 共享节点
    Animated = 4,    // 动画节点
    Movable = 8,     // 可移动节点
    Toggle = 16,     // 开关节点
    Material = 32,   // 材质节点
};
ENUM_CLASS_FLAGS(ENodeType)
```

### 导入流程

典型的导入流程（以 VRED 为例）：

```
1. FDatasmithVREDTranslator::IsSourceSupported()
   → 读取 FBX 文件头，检查 ApplicationName == "VRED"

2. FDatasmithVREDTranslator::LoadScene()
   → 创建 FDatasmithVREDImporter
   → OpenFile() → ParseFbxFile() + ParseAuxFiles()
   → SendSceneToDatasmith() → ConvertNode() + ConvertMaterial() + ConvertAnimBlock()

3. FDatasmithVREDTranslator::LoadStaticMesh()
   → GetGeometriesForMeshElementAndRelease() 返回 FMeshDescription
```

### 场景处理器功能

`FDatasmithFBXSceneProcessor` 提供以下场景优化操作：

```cpp
// 去重
void FindDuplicatedMaterials();  // 查找并合并重复材质
void FindDuplicatedMeshes();     // 查找并合并重复网格

// 清理
void RemoveLightMapNodes();      // 移除 LightMap 辅助节点
void RemoveInvisibleNodes();     // 移除不可见节点
void RemoveEmptyNodes();         // 移除空节点
void RemoveTempNodes();          // 移除 VRED 导出辅助几何

// 优化
void FindPersistentNodes();      // 标记不应合并的节点
void SimplifyNodeHierarchy();    // 折叠节点层级
void FixNodeNames();             // 修复节点名称（处理空白字符）
void FixMeshNames();             // 修复无效网格名称（如 'AUX', 'CON'）

// 拆分（坐标系适配）
void SplitControlNodes();        // 拆分控制节点
void SplitLightNodes();          // 拆分灯光节点（VRED: -Z → UE: +X）
void SplitCameraNodes();         // 拆分摄像机节点
```

## Python 用法

插件提供了 Python API 用于脚本化导入。测试脚本位于 `Resources/PythonAPI/`。

### VRED 场景导入

```python
import unreal

# 配置导入选项
base_options = unreal.DatasmithImportBaseOptions()
base_options.set_editor_property('include_geometry', True)
base_options.set_editor_property('include_material', True)
base_options.set_editor_property('include_animation', True)

vred_options = unreal.DatasmithVREDImportOptions()
vred_options.set_editor_property('import_var', True)
vred_options.set_editor_property('import_light_info', True)
vred_options.set_editor_property('import_clip_info', True)

# 方式一：直接导入到场景
unreal.VREDLibrary.import_("scene.fbx", "/Game/Imported", base_options, None, True)

# 方式二：两阶段导入（可修改中间数据）
scene = unreal.DatasmithVREDSceneElement.construct_datasmith_scene_from_file(
    "scene.fbx", "/Game/Imported", base_options, vred_options
)
# 查询场景信息
print(len(scene.get_all_mesh_actors()))
print(len(scene.get_all_variants()))
print(len(scene.get_all_anim_clips()))

# 修改后导入
result = scene.import_scene()
```

### DeltaGen 场景导入

```python
import unreal

dg_options = unreal.DatasmithDeltaGenImportOptions()
dg_options.set_editor_property('import_var', True)
dg_options.set_editor_property('import_pos', True)
dg_options.set_editor_property('import_tml', True)
dg_options.set_editor_property('shadow_texture_mode', unreal.EShadowTextureMode.AMBIENT_OCCLUSION)

scene = unreal.DatasmithDeltaGenSceneElement.construct_datasmith_scene_from_file(
    "scene.fbx", "/Game/Imported", base_options, dg_options
)
# 查询场景信息
print(len(scene.get_all_animation_timelines()))
print(len(scene.get_all_variants()))

result = scene.import_scene()
```

## 辅助文件格式

### VRED 辅助文件

| 文件 | 解析器 | 说明 |
|---|---|---|
| `.mats` | `FDatasmithVREDAuxFiles::ParseMatsFile()` | 材质参数，覆盖 FBX 中的材质信息 |
| `.var` | `FDatasmithVREDAuxFiles::ParseVarFile()` | 变体定义（几何/材质/变换/灯光/摄像机/变体集） |
| `.lights` | `FDatasmithVREDAuxFiles::ParseLightsFile()` | 灯光额外参数（温度、衰减、IES 等） |
| `.clips` | `FDatasmithVREDAuxFiles::ParseClipsFile()` | 动画剪辑和动画块组合 |

### DeltaGen 辅助文件

| 文件 | 解析器 | 说明 |
|---|---|---|
| `.var` | `FDatasmithDeltaGenAuxFiles::ParseVarFile()` | 变体定义（几何/摄像机/包/切换对象/对象集） |
| `.pos` | `FDatasmithDeltaGenAuxFiles::ParsePosFile()` | POV 状态（可见性、切换选择、材质分配） |
| `.tml` | `FDatasmithDeltaGenAuxFiles::ParseTmlFile()` | 时间线动画（平移/旋转/缩放/中心，支持常量/线性/贝塞尔插值） |

## 变体系统

### VRED 变体类型

```cpp
enum class EVREDCppVariantType : uint8
{
    Unsupported,
    Camera,      // 摄像机变体（位置+旋转）
    Geometry,    // 几何变体（可见/隐藏网格列表）
    VariantSet,  // 变体集（组合其他变体）
    Material,    // 材质变体
    Transform,   // 变换变体
    Light        // 灯光变体
};
```

### DeltaGen 变体类型

```cpp
enum class EDeltaGenVarDataVariantSwitchType : uint8
{
    Unsupported,
    Camera,       // 摄像机变体
    Geometry,     // 几何变体
    Package,      // 包变体（组合多个变体集的选择）
    SwitchObject, // 切换对象变体
    ObjectSet     // 对象集变体（变换/可见性/材质）
};
```

## 动画系统

### VRED 动画

VRED 使用 **AnimNode → AnimBlock → AnimCurve** 的层级结构：

- `FDatasmithFBXSceneAnimNode`：包含多个 AnimBlock
- `FDatasmithFBXSceneAnimBlock`：一组变换/可见性曲线
- `FDatasmithFBXSceneAnimCurve`：单个属性的动画曲线（带 DSID 标识）

通过 `.clips` 文件定义 **AnimClip**，组合多个 AnimBlock 为复杂动画序列。`FDatasmithVREDClipProcessor` 负责处理嵌套剪辑延迟和翻转动画。

### DeltaGen 动画

DeltaGen 使用 `.tml` 文件定义时间线动画：

- `FDeltaGenTmlDataTimeline`：一个时间线，包含多个动画
- `FDeltaGenTmlDataTimelineAnimation`：针对一个目标节点的动画
- `FDeltaGenTmlDataAnimationTrack`：单个属性轨道（平移/旋转/缩放/中心）

支持三种插值类型：常量（`FConstInterpolator`）、线性（`FLinearInterpolator`）、贝塞尔三次（`FCubicInterpolator`）。`FDatasmithDeltaGenAnimationInterpolator` 提供了直接使用贝塞尔控制点的插值实现。

## 模块依赖

### DatasmithFBXTranslator

| 模块 | 用途 |
|---|---|
| `Core` | 基础类型和容器 |
| `CoreUObject` | UObject 系统 |
| `DatasmithCore` | Datasmith 核心类型定义 |
| `DatasmithContent` | Datasmith 内容资产（公开依赖） |
| `DatasmithTranslator` | Translator 接口（公开依赖） |
| `EditorFramework` | 编辑器框架 |
| `Engine` | 引擎核心 |
| `LevelSequence` | 关卡序列支持 |
| `MeshDescription` | 网格体中间表示 |
| `StaticMeshDescription` | 静态网格属性 |
| `UnrealEd` | FBX SDK 封装（UnFbx） |
| `FBX` | FBX SDK（第三方库） |

### DatasmithVREDTranslator

| 模块 | 用途 |
|---|---|
| `DatasmithFBXTranslator` | FBX 翻译器基类（公开依赖） |
| `XmlParser` | XML 解析（辅助文件） |

### DatasmithDeltaGenTranslator

| 模块 | 用途 |
|---|---|
| `DatasmithFBXTranslator` | FBX 翻译器基类（公开依赖） |
| `XmlParser` | XML 解析（辅助文件） |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 |
|---|---|---|
| 2025-03-13 | `b059f7b` | 修复 trivial unreachable code warnings |
| 2024-10-02 | `0a14cf0` | 更新 VRED Python exporter 以支持 VRED API 变更，添加 APIV2 文件夹 |
| 2024-09-23 | `3ac6607` | 修复大量 FString::Printf 格式错误 |

### 维护评价

- **创建时间**：2019 年 10 月，随 UE4 Datasmith 企业版功能一起引入
- **维护频率**：低频维护，最近一次实质性功能更新是 2024 年 10 月的 VRED API V2 支持
- **维护状态**：**维护中** — 近 6 个月内有编译修复更新，2024 年有功能性更新（VRED exporter 适配）
- **已知限制**：
  - `EnabledByDefault=false`，需要手动在插件管理器中启用
  - `LoadLevelSequence()` 方法在两个 Translator 中均被注释掉，返回 `false`，说明关卡序列的按需加载尚未完成
  - DeltaGen 的 `EShadowTextureMode` 提供了阴影纹理的多种处理方式，但效果取决于源数据质量
- **推荐**：如果你的工作流涉及 VRED 或 DeltaGen → **必须使用**；否则无需启用

## VRED Python Exporter

插件附带 VRED Python 脚本（位于 `Resources/VREDPlugin/`），用于在 VRED 端导出 Datasmith 兼容的辅助文件：

- **APIV1/**：兼容 VRED 旧版 API
- **APIV2/**：兼容 VRED 新版 API（2024 年 10 月添加）

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/DatasmithFBXImporter)
- [VRED Python Exporter (APIV2)](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/DatasmithFBXImporter/Resources/VREDPlugin/APIV2)
- [DeltaGen Python Exporter](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/DatasmithFBXImporter/Resources/PythonAPI)
- 依赖插件：[DatasmithImporter](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/DatasmithImporter)，[DatasmithContent](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/DatasmithContent)
