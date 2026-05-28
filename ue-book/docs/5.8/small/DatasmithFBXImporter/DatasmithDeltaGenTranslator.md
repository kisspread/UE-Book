# Datasmith FBX Importer

> Adds support for importing content from DeltaGen and VRED into Unreal Engine

| 属性 | 值 |
|---|---|
| 中文名 | Datasmith FBX 导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DatasmithVREDTranslator` (Editor), `DatasmithDeltaGenTranslator` (Editor), `DatasmithFBXTranslator` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithFBXImporter) | |

## 用途

这个插件并非一个通用的 FBX 导入器（UE 自带的 FBX 导入功能已经很强大），而是 **Datasmith 框架下针对两款特定汽车设计软件——DeltaGen 和 VRED 的专用导入器**。它解决了将这些软件创建的复杂场景（包含大量变体、精确的动画、材质配置）无缝导入到 Unreal Engine 进行实时渲染、设计评审和市场营销内容制作的问题。插件的核心价值在于解析 DeltaGen（`.var`, `.pos`, `.tml`）和 VRED 的专有辅助文件，并将它们转换为 UE 中的变体集（Level Variant Sets）、动画序列（Level Sequence）和材质实例。

## 使用场景

- **汽车设计评审**：你在 DeltaGen 或 VRED 中完成了车辆内饰/外饰的多个设计方案（变体），需要导入 UE 中让不同部门的同事通过 VR 进行交互式评审。此插件能将每个方案的几何体可见性、材质、相机位置等精确导入并转换为可切换的变体。
- **市场营销素材制作**：你需要基于设计数据创建高质量的渲染视频或交互式配置器。插件导入的动画时间线（TML）和状态（POS）可以直接在 Sequencer 中用于制作动态展示内容。
- **工艺流程集成**：将 DeltaGen/VRED 作为前端建模工具，UE 作为后端实时引擎，通过 Datasmith 流程进行自动化或半自动化的资产同步。

## 蓝图用法

该插件的核心是编辑器导入模块，不直接暴露运行时蓝图节点。主要配置通过导入对话框或项目设置完成。

### 核心类

| 类 | 说明 |
|---|---|
| `UDatasmithDeltaGenImportOptions` | DeltaGen 导入的详细配置选项类。在蓝图中可通过对象引用来访问和修改。 |

### 使用示例（蓝图描述）

由于是编辑器插件，典型用法是在内容浏览器中右键点击 FBX 文件 -> “Import Into Level...”，然后在弹出的 Datasmith 导入选项面板中配置 DeltaGen 相关的选项（如是否导入变体、动画文件等）。这些选项最终会实例化一个 `UDatasmithDeltaGenImportOptions` 对象。

## C++ 用法

### 头文件引入

```cpp
// 要使用 DeltaGen 翻译器模块
#include “DatasmithDeltaGenTranslatorModule.h” // 公共头文件
```

### 基本用法

这个插件主要由 Datasmith 管道内部调用，开发者很少直接与其交互。最接近的用法是通过翻译器模块检查可用性。

```cpp
// 检查 DeltaGen 翻译器模块是否已加载（通常在需要条件性功能时使用）
if (IDatasmithDeltaGenTranslatorModule::IsAvailable())
{
    UE_LOG(LogTemp, Log, TEXT(“Datasmith DeltaGen Translator is ready.”));
    // 可以在此处执行依赖于该翻译器的功能逻辑
}
```

### 进阶用法

从 `FDatasmithDeltaGenImporter` 和 `FDatasmithDeltaGenTranslator` 的接口可以看出，高级用户理论上可以自定义或扩展导入流程，但这需要深入理解 Datasmith 的内部架构，通常不推荐。

## Demo 示例

以下是一个理论上的最小示例，展示如何获取 DeltaGen 翻译器模块并查询其状态。请注意，这仅用于演示模块访问，实际场景中你通常无需手动操作这些类。

### MyActor.h
```cpp
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyActor.generated.h"

UCLASS()
class AMyActor : public AActor
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;

    UFUNCTION(BlueprintCallable, Category = “Datasmith”)
    bool IsDeltaGenTranslatorReady() const;
};
```

### MyActor.cpp
```cpp
#include "MyActor.h"
#include "DatasmithDeltaGenTranslatorModule.h”

void AMyActor::BeginPlay()
{
    Super::BeginPlay();
    IsDeltaGenTranslatorReady();
}

bool AMyActor::IsDeltaGenTranslatorReady() const
{
    return IDatasmithDeltaGenTranslatorModule::IsAvailable();
}
```

## 模块依赖

该插件自身依赖以下插件/模块，你的项目模块若需使用其功能，通常不需要直接依赖它，而是依赖 Datasmith 核心。

| 模块/插件 | 用途 |
|---|---|
| `DatasmithImporter` | 核心的 Datasmith 导入框架 |
| `DatasmithContent` | Datasmith 相关的资产类型定义 |
| `DatasmithFBXTranslator` | 基础的 FBX 到 Datasmith 场景的转换逻辑，是 DeltaGen 和 VRED 翻译器的基础 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下，双精度常量截断为浮点数所产生的警告。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 `UE_LOG` 宏迁移到新的 `UE_LOGF` 宏。 |
| 2026-02-03 | `88ba268b` | Fix unreachable code errors | 修复不可达代码错误。 |
| 2025-03-13 | `b059f7b4` | Fix trivial unreachable code warnings. | 修复轻微的不可达代码警告。 |
| 2024-10-02 | `0a14cf0e` | Update VRED python exporter to support API changes in VRED | 更新 VRED 的 Python 导出器以适配 VRED 的 API 变更。 |

### 维护评价

- **年龄**：插件创建于 2019 年，已有约 7 年历史。
- **活跃度**：近期仍有更新，主要集中在 **编译器警告修复、宏迁移和对外部软件（VRED）API 变更的适配**。这些属于维护性更新，表明插件仍在官方的维护范围内，以确保其能在新版本 UE 中编译和运行。
- **稳定性**：没有迹象表明该插件被废弃，但自创建以来，其核心功能集似乎已稳定。
- **推荐**：如果你的项目工作流**必须**使用 DeltaGen 或 VRED 的资产，并且需要其专有的变体和动画数据，那么这个插件是**必需且推荐**的。对于其他通用的 FBX 导入需求，应使用 UE 内置的 FBX 导入器。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithFBXImporter)
- [Datasmith 官方文档](https://docs.unrealengine.com/5.0/en-US/datasmith-import-process-in-unreal-engine/) (Datasmith 总体流程文档)