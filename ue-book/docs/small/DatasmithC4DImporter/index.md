# Datasmith C4D Importer

> Adds support for importing content from Cinema4D applications into Unreal Engine

| 属性 | 值 |
|---|---|
| 分类 | Importers |
| 默认启用 | false |
| 包含内容 | false |
| 模块 | DatasmithC4DTranslator (Runtime) |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 👴 老古董(>5年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/DatasmithC4DImporter) | |

## 用途

这是一个 Datasmith 翻译器插件，让 Unreal Engine 能够直接导入 Cinema 4D（.c4d）文件。它通过 Maxon 提供的 Melange SDK 读取 C4D 文档，将场景层次结构、网格体、材质、纹理、灯光、摄像机和动画转换为 Datasmith 中间表示，再由 Datasmith 管线导入到 UE 中。

该插件解决的核心问题是：Cinema 4D 是建筑可视化和影视行业中广泛使用的 DCC 工具，但其原生 .c4d 格式 UE 无法直接读取。DatasmithC4DImporter 填补了这一空白，使用户无需先将 C4D 场景导出为 FBX 或其他中间格式。

**注意：** 该插件依赖 Maxon Cinema 4D Melange SDK（一个免费的 C4D 文件读取库）。如果 Melange SDK 未安装，插件在编译时会定义 `_MELANGE_SDK_` 宏为未定义状态，导致翻译器自动禁用。

## 使用场景

- 你在用 Cinema 4D 制作建筑可视化模型，需要将场景导入 UE 做实时渲染 → 启用此插件，直接拖放或通过 Datasmith 导入 .c4d 文件
- 你在用 C4D 制作产品展示动画，需要在 UE 中保留动画和摄像机数据 → 此插件支持导入 LevelSequence 动画
- 你需要批量导入 C4D 资产到 UE 项目 → 通过 Datasmith 管线自动化导入

## 蓝图用法

该插件不暴露任何 BlueprintCallable 函数。它是纯翻译器（Translator）插件，通过 Datasmith 导入管线工作，用户通过编辑器的 **File > Import** 或 Datasmith 导入按钮交互。

### 导入选项

导入 C4D 文件时，编辑器会弹出导入选项面板，提供以下设置（定义在 `UDatasmithC4DImportOptions`）：

| 选项 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| Import Mesh With No Vertex | bool | false | 是否导入无顶点的空网格体 |
| Clean the Scene of Empty Actors With Only One Child | bool | false | 移除只有一个子节点的空 Actor，简化场景层次 |
| Generate the Normals | bool | false | 忽略 Melange 提供的法线，由 Datasmith 重新生成 |
| Scale the Entire Scene | float | 1.0 | 缩放整个场景（解决 C4D 双精度到 UE 单精度的精度退化问题） |
| Export to .udatasmith | bool | false | 导入同时将场景导出为 .udatasmith 文件（仅编辑器） |

## C++ 用法

该插件是 Datasmith 翻译器系统的实现，通常不需要用户直接编写 C++ 代码。以下信息供需要扩展或调试的开发者参考。

### 核心类

- **`FDatasmithC4DTranslator`** — 实现 `IDatasmithTranslator` 接口，是 Datasmith 框架发现和调用 C4D 导入的入口
- **`FDatasmithC4DImporter`** — 实际的导入逻辑，使用 Melange SDK 读取 .c4d 文件并转换为 Datasmith 元素
- **`UDatasmithC4DImportOptions`** — UCLASS 导入选项，暴露到编辑器 UI

### 导入流程

1. Datasmith 框架通过 `IDatasmithTranslator::Initialize()` 发现翻译器
2. `FDatasmithC4DTranslator::LoadScene()` 调用 `FDatasmithC4DImporter::OpenFile()` 打开 .c4d 文件
3. `ProcessScene()` 遍历 C4D 场景层次结构，导入：
   - 网格体（PolygonObject → IDatasmithMeshElement）
   - 材质和纹理（Material → IDatasmithMaterialInstanceElement）
   - 灯光、摄像机
   - 动画关键帧 → IDatasmithLevelSequenceElement
   - 实例化对象（Oinstance）的层次映射
4. `LoadStaticMesh()` 按需提供 MeshDescription 数据

### 头文件引入

```cpp
// 引入翻译器接口
#include "DatasmithTranslator.h"

// 引入 C4D 导入选项
#include "DatasmithC4DImportOptions.h"
```

### Melange SDK 条件编译

该插件大量使用条件编译。如果 Melange SDK 未找到，所有导入功能都会被编译为空实现：

```cpp
#if !defined(_MELANGE_SDK_)
    virtual void Initialize(FDatasmithTranslatorCapabilities& OutCapabilities) override
    {
        OutCapabilities.bIsEnabled = false;  // SDK 未安装时自动禁用
    }
#else
    // ... 实际实现
#endif
```

## Demo 示例

由于该插件是编辑器翻译器，没有独立的 C++ API 示例。使用方式：

1. 启用插件：**Edit > Plugins > Datasmith C4D Importer > Enable**
2. 重启编辑器
3. **File > Import** 选择 .c4d 文件，或使用 Datasmith 导入按钮
4. 在导入选项面板中调整设置
5. 点击导入

## 模块依赖

从 Build.cs 的依赖关系提取：

| 模块 | 用途 |
|---|---|
| `DatasmithContent` | Datasmith 导入后的资产数据类型 |
| `DatasmithTranslator` | 翻译器接口基类 |
| `DatasmithCore` | Datasmith 核心数据模型 |
| `MeshDescription` | UE 网格体中间表示 |
| `StaticMeshDescription` | 静态网格体扩展描述 |
| `Imath` | OpenEXR 数学库 |
| `MelangeSDK` | Cinema 4D Melange SDK（条件依赖，需 SDK 存在） |
| `DatasmithExporter` | .udatasmith 导出功能（仅编辑器） |

**外部依赖：** 需要安装 Maxon Cinema 4D Melange SDK。SDK 路径优先查找 `Engine/Restricted/NotForLicensees/Source/ThirdParty/Enterprise/Melange/`，否则查找环境变量 `Melange_SDK`。

**平台限制：** 仅支持 Win64 和 Mac。Win64 ARM64 目前不支持（无 Melange SDK）。

## 维护状态

### 近期更新

| 日期 | Hash | 说明 |
|---|---|---|
| 2025-03-11 | `31fb4d5d` | 修复 unreachable code warnings（break after return 等） |
| 2024-09-23 | `3ac66072` | 修复大量 FString::Printf 格式错误 |
| 2024-09-23 | `29238868` | WinArm64 SymsLib 更新及 .sln 更新 |

### 维护评价

- **创建时间：** 2019-10-04，已超过 6 年
- **最近更新：** 2025-03-11，最近一次更新是代码质量修复（unreachable code warnings），非功能性更新
- **维护状态：** 维护中 — 仍在跟随 UE 版本更新做编译适配，但无新功能开发
- **已知限制：**
  - 依赖 Melange SDK，需要单独安装
  - 不支持 Win64 ARM64
  - 仅 Runtime 类型模块，无蓝图接口
  - C4D 的 double 精度到 UE 的 float 精度转换可能导致面退化（可通过 ScaleVertices 选项缓解）
- **推荐：** ✅ 推荐使用。对于需要从 Cinema 4D 导入内容的工作流，这是官方支持的首选方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/DatasmithC4DImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)
- [DatasmithImporter 依赖插件](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/DatasmithImporter)
