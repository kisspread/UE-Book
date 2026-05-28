# Datasmith Content

> Content for Datasmith Importer.

| 属性 | 值 |
|---|---|
| 中文名 | Datasmith内容库 |
| 分类 | Importers |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（Datasmith内容资产，如材质、纹理） |
| 模块 | `DatasmithContent` (Runtime), `DatasmithContentEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2017-12-08 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithContent) | |

## 用途

DatasmithContent 是 **Datasmith 导入器**的核心配套内容插件。它并非一个独立的导入器，而是一个**内容资源库**，主要解决以下问题：

1.  **提供标准化基础资产**：当通过 Datasmith 插件从 CAD、BIM 或其他 3D 软件导入数据时，会使用该插件中的基础材质和纹理来构建导入对象，确保统一的视觉表现和渲染质量。
2.  **支持元数据和场景结构**：包含用于定义 Datasmith 场景结构（如 Actor 层级、元数据标签）的 Blueprint 和核心类，是理解与操作 Datasmith 场景的基石。
3.  **解耦依赖**：通过将内容独立为插件，使得仅包含从 Datasmith 导出资产的项目（如通过 Datasmith Runtime 播放），无需安装完整的 Datasmith Importer 编辑器插件也能正确加载这些内容资产。

简单来说，**DatasmithContent 是 Datasmith 导入流水线的“资源字典”和“说明书”**，它定义了导入数据如何被转化为 Unreal Engine 中的可运行资产。

## 使用场景

- **建筑可视化**：将 Revit、ArchiCAD 等 BIM 软件的模型通过 Datasmith 导入后，需要该插件提供的材质来正确表现建筑构件。
- **工业设计与制造**：导入 CATIA、NX、SolidWorks 等 CAD 软件的机械零件，其材质和元数据依赖于本插件。
- **数字孪生与XR**：使用 Datasmith Runtime 进行实时数据驱动的场景播放时，项目必须包含此插件以解析导入的资产和场景逻辑。
- **内容迁移**：当需要将一个使用 Datasmith 导入的资产迁移至另一个项目时，目标项目必须启用此插件，否则材质和场景结构会丢失。

## 模块列表

| 模块 | 类型 | 说明 |
|---|---|---|
| `DatasmithContent` | Runtime | **核心运行时模块**。包含用于构建 Datasmith 场景的核心类、蓝图库以及资产定义。 |
| `DatasmithContentEditor` | Editor | **编辑器扩展模块**。提供在编辑器中可视化、调试和处理 Datasmith 资产的工具。 |

## 蓝图用法

蓝图功能主要通过 `DatasmithContent` 模块中的蓝图函数库暴露。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Datasmith Scene from Level` | 从当前或指定关卡中获取 `UDatasmithScene` 对象。 | `UDatasmithContentBlueprintLibrary` |
| `Get Child Components` | 获取 `UDatasmithScene` 下指定层级的子组件列表。 | `UDatasmithContentBlueprintLibrary` |
| `Get Metadata` | 获取特定 `UDatasmithScene` 或其子组件的元数据（键值对）。 | `UDatasmithContentBlueprintLibrary` |
| `Set Metadata` | 设置 `UDatasmithScene` 或其子组件的元数据。 | `UDatasmithContentBlueprintLibrary` |
| `Get Metadata Keys` | 获取指定对象上所有元数据键的数组。 | `UDatasmithContentBlueprintLibrary` |

### 使用示例（蓝图描述）

要从当前关卡获取 Datasmith 场景并读取一个名为 `MaterialName` 的元数据：
1.  使用 `Get Datasmith Scene from Level` 节点（输入引脚可留空表示当前关卡）。
2.  将其返回值连接到 `Get Metadata` 节点的 `Target` 输入。
3.  在 `Metadata Key` 输入引脚填入 `MaterialName`。
4.  `Out Value` 输出引脚将返回该元数据对应的字符串值。

## C++ 用法

### 头文件引入

```cpp
// 运行时模块核心头文件
#include "DatasmithContent.h"
// 访问特定的Datasmith资产类
#include "Assets/DatasmithScene.h"
#include "Components/DatasmithSceneComponent.h"
```

### 基本用法

以下示例展示了如何在C++中获取Datasmith场景并操作元数据。

```cpp
// 引擎核心头文件
#include "Engine/World.h"
#include "DatasmithScene.h"

// 在Actor或Component中
void AMyDatasmithActor::PrintDatasmithMetadata()
{
    UWorld* World = GetWorld();
    if (!World) return;

    // 使用DatasmithContent模块提供的库函数获取场景
    UDatasmithScene* Scene = UDatasmithContentBlueprintLibrary::GetDatasmithSceneFromLevel(World->PersistentLevel);

    if (Scene)
    {
        // 读取元数据
        FString MaterialValue;
        Scene->GetMetadata(TEXT("MaterialName"), MaterialValue);
        UE_LOG(LogTemp, Log, TEXT("Material Name: %s"), *MaterialValue);

        // 设置元数据
        Scene->SetMetadata(TEXT("Version"), TEXT("1.2"));
    }
}
```
*（示例基于模块文档中描述的 `UDatasmithContentBlueprintLibrary` API）*

## Demo 示例

以下是一个最小化的 Actor 类，用于在 BeginPlay 时打印所关联的 Datasmith 场景信息。

**MyDatasmithReader.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "DatasmithScene.h" // 引入Datasmith核心类
#include "MyDatasmithReader.generated.h"

UCLASS()
class AMyDatasmithReader : public AActor
{
    GENERATED_BODY()

public:
    AMyDatasmithReader();

protected:
    virtual void BeginPlay() override;

private:
    // 可以在编辑器中指向一个Datasmith场景资产
    UPROPERTY(EditAnywhere, Category="Datasmith")
    UDatasmithScene* MyScene;
};
```

**MyDatasmithReader.cpp**
```cpp
#include "MyDatasmithReader.h"
#include "DatasmithContentBlueprintLibrary.h" // 引入蓝图库，用于静态函数

AMyDatasmithReader::AMyDatasmithReader()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyDatasmithReader::BeginPlay()
{
    Super::BeginPlay();

    UDatasmithScene* SceneToRead = MyScene;

    // 如果未手动指定，则尝试从当前关卡获取
    if (!SceneToRead)
    {
        SceneToRead = UDatasmithContentBlueprintLibrary::GetDatasmithSceneFromLevel(GetLevel());
    }

    if (SceneToRead)
    {
        UE_LOG(LogTemp, Warning, TEXT("Loaded Datasmith Scene: %s"), *SceneToRead->GetName());

        // 遍历并打印子组件（简化示例）
        for (USceneComponent* Child : SceneToRead->GetChildrenComponents(false))
        {
            if (UDatasmithSceneComponent* DsComp = Cast<UDatasmithSceneComponent>(Child))
            {
                UE_LOG(LogTemp, Log, TEXT("  - Scene Component: %s"), *DsComp->GetName());
                // 可以进一步获取DsComp的元数据等信息
            }
        }
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("No Datasmith Scene found for this actor/level."));
    }
}
```

## 模块依赖

要使用 DatasmithContent 插件的功能，你的模块需要依赖以下模块（根据模块文档推断）：

| 模块 | 用途 |
|---|---|
| `DatasmithContent` | 依赖本插件的核心运行时模块，以使用其类和蓝图库。 |
| `DatasmithRuntime` | （如果使用运行时加载功能）用于运行时加载和处理 Datasmith 文件。 |
| `RenderCore` | （可能）如果操作涉及材质或渲染资产。 |
| `FunctionalTesting` | （仅在测试中）如果使用其提供的测试资产。 |

**无特殊依赖（仅标准 Core/Engine/Slate 等）**：对于大多数用例，仅需依赖 `DatasmithContent` 模块本身。具体依赖需查阅 `DatasmithContent.Build.cs` 和 `DatasmithContentEditor.Build.cs` 文件。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从UE_LOG迁移至新的UE_LOGF宏。 |
| 2026-03-24 | `69a7403a` | Fixed cooking failure duue to ensure | 修复因ensure导致的打包（Cooking）失败问题。 |
| 2026-03-24 | `76f61985` | Deprecated UDatasmithStaticMeshCADImportData class... | 废弃了不再使用且存在安全隐患的UDatasmithStaticMeshCADImportData类。 |
| 2026-03-23 | `06410f9f` | [Backout] - CL52072615 | 回退了之前的某个变更（CL52072615）。 |
| 2026-03-23 | `c14d73ba` | Deprecated UDatasmithStaticMeshCADImportData class... | 首次尝试废弃UDatasmithStaticMeshCADImportData类，后因问题被回退。 |

### 维护评价

- **活跃维护**：插件仍在积极维护中。最近一次更新在2026年4月，涉及日志宏的迁移，表明团队在跟进引擎内部的基础架构改进。
- **代码质量与安全**：近期的更新集中在**代码健康度和安全性**上，如移除废弃类、修复打包失败和日志宏迁移。没有重大新功能引入，说明该插件已进入**成熟稳定期**。
- **推荐使用**：作为Datasmith生态的基石插件，它是使用任何Datasmith导入资产的**必需品**。由于其核心且稳定的地位，可以放心在生产项目中使用。唯一需要注意的是，其内部类API可能随引擎版本进行小幅度的废弃和清理（如近期所示），但通常不会影响通过蓝图或基础C++接口的使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithContent)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithContent/Tests)