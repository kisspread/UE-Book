# Datasmith Importer

> Importer for Datasmith files.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DatasmithExternalSource` (Runtime), `DatasmithImporter` (Runtime), `DatasmithNativeTranslator` (Runtime), `DatasmithTranslator` (Runtime), `DirectLinkExtension` (Runtime), `DirectLinkExtensionEditor` (Runtime), `DirectLinkTest` (Runtime), `ExternalSource.build` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/DatasmithImporter) | |

## 用途

Datasmith Importer 是一个用于将外部设计软件（如 CAD、BIM、DCC 等）生成的复杂场景和资产导入 Unreal Engine 的企业级解决方案。它不仅仅是一个简单的文件导入器，更是一个完整的数据转换和同步框架。其核心价值在于：

1.  **格式转换**：将 `.udatasmith`、`.udatassembly` 等 Datasmith 格式文件，以及通过 DirectLink 协议实时传输的数据，转换为 UE 可识别的资产（静态网格体、材质、蓝图、关卡等）。
2.  **数据保真**：在转换过程中尽可能保留原始设计软件中的层级结构、元数据、材质属性和几何信息，确保在 UE 中的可视化效果与原始设计一致。
3.  **实时同步**：通过 DirectLink 技术，支持与支持该协议的外部软件（如 Autodesk Revit, 3ds Max, SketchUp 等）建立实时连接，实现设计变更的即时同步到 UE 中，极大提升了设计评审和可视化的效率。
4.  **资产管理**：提供了一套工具来管理导入的资产，包括更新、重新导入、以及通过内容浏览器过滤器快速定位 Datasmith 导入的资产。

## 使用场景

-   **建筑可视化 (ArchViz)**：建筑师使用 Revit 或 SketchUp 完成设计后，通过 Datasmith 将完整的建筑模型、材质和灯光信息导入 UE，用于创建高质量的实时漫游、VR 体验或营销视频。
-   **工业设计与制造**：工程师使用 CATIA、SolidWorks 或 NX 完成产品设计后，通过 Datasmith 导入 UE，用于创建交互式产品配置器、装配指导或虚拟培训模拟。
-   **设计评审与协作**：设计团队利用 DirectLink 的实时同步功能，在 UE 中实时查看外部软件中的设计修改，进行跨部门的协同评审，无需反复导出和导入文件。
-   **大型场景合成**：将来自不同专业软件（如结构、MEP、景观）的多个 Datasmith 文件合并到同一个 UE 关卡中，构建完整的数字孪生或虚拟世界。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `DisplayDirectLinkSourcesDialog` | 弹出一个对话框，让用户从可用的 DirectLink 外部源中选择一个。返回选中的源对象，若用户取消则返回空。 | `UDirectLinkExtensionEditorModule` |

### 使用示例（蓝图描述）

1.  **触发导入对话框**：在某个蓝图（例如，一个自定义的编辑器工具蓝图或关卡蓝图）中，调用 `DisplayDirectLinkSourcesDialog` 节点。
2.  **处理返回值**：将该节点的返回值（一个 `DirectLinkExternalSource` 对象）连接到一个分支节点。
3.  **执行后续操作**：如果返回值有效（非空），则可以使用该对象进行后续操作，例如触发从该源进行数据同步或导入。如果返回值为空，则表示用户取消了选择，可以执行其他逻辑或直接结束。

## C++ 用法

### 头文件引入

```cpp
#include "DirectLinkExtensionEditorModule.h"
```

### 基本用法

获取 `DirectLinkExtensionEditor` 模块实例并显示源选择对话框。

```cpp
// 检查模块是否可用
if (IDirectLinkExtensionEditorModule::IsAvailable())
{
    // 获取模块单例
    IDirectLinkExtensionEditorModule& DirectLinkEditorModule = IDirectLinkExtensionEditorModule::Get();
    
    // 显示 DirectLink 源选择对话框
    TSharedPtr<UE::DatasmithImporter::FDirectLinkExternalSource> SelectedSource = DirectLinkEditorModule.DisplayDirectLinkSourcesDialog();
    
    if (SelectedSource.IsValid())
    {
        // 用户选择了一个源，可以在此处进行后续操作，例如：
        // - 获取源的详细信息
        // - 触发从该源的数据导入
        UE_LOG(LogTemp, Log, TEXT("Selected DirectLink Source: %s"), *SelectedSource->GetSourceName());
    }
    else
    {
        // 用户取消了对话框
        UE_LOG(LogTemp, Warning, TEXT("DirectLink source selection was cancelled."));
    }
}
```

### 进阶用法

结合 `DirectLinkExtension` 模块的管理器功能，对选定的源进行操作。

```cpp
#include "DirectLinkExtensionModule.h"
#include "DirectLinkExtensionEditorModule.h"

void ImportFromSelectedDirectLinkSource()
{
    if (!IDirectLinkExtensionEditorModule::IsAvailable() || !IDirectLinkExtensionModule::IsAvailable())
    {
        return;
    }

    IDirectLinkExtensionEditorModule& EditorModule = IDirectLinkExtensionEditorModule::Get();
    IDirectLinkExtensionModule& ExtensionModule = IDirectLinkExtensionModule::Get();
    
    // 显示对话框让用户选择源
    TSharedPtr<UE::DatasmithImporter::FDirectLinkExternalSource> Source = EditorModule.DisplayDirectLinkSourcesDialog();
    
    if (Source.IsValid())
    {
        // 通过管理器获取与该源相关的更多操作接口
        UE::DatasmithImporter::IDirectLinkManager& Manager = ExtensionModule.GetManager();
        
        // 此处可以调用 Manager 的方法来与选定的源进行交互
        // 例如，检查连接状态、触发同步等（具体方法需查阅 IDirectLinkManager 接口）
        // Manager.SomeMethodForSource(Source);
    }
}
```

## Demo 示例

一个简单的 Actor，用于在编辑器中通过按钮触发 DirectLink 源选择对话框。

**DirectLinkDemoActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "DirectLinkDemoActor.generated.h"

UCLASS()
class ADirectLinkDemoActor : public AActor
{
    GENERATED_BODY()
    
public:
    ADirectLinkDemoActor();

    // 在编辑器中调用此函数以显示 DirectLink 源选择对话框
    UFUNCTION(BlueprintCallable, CallInEditor, Category = "DirectLink Demo")
    void SelectDirectLinkSource();
};
```

**DirectLinkDemoActor.cpp**
```cpp
#include "DirectLinkDemoActor.h"
#include "DirectLinkExtensionEditorModule.h"

ADirectLinkDemoActor::ADirectLinkDemoActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void ADirectLinkDemoActor::SelectDirectLinkSource()
{
    if (IDirectLinkExtensionEditorModule::IsAvailable())
    {
        IDirectLinkExtensionEditorModule& Module = IDirectLinkExtensionEditorModule::Get();
        TSharedPtr<UE::DatasmithImporter::FDirectLinkExternalSource> Source = Module.DisplayDirectLinkSourcesDialog();
        
        if (Source.IsValid())
        {
            UE_LOG(LogTemp, Display, TEXT("User selected DirectLink source: %s"), *Source->GetSourceName());
            // 在这里添加对选中源的处理逻辑
        }
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("DirectLinkExtensionEditor module is not available."));
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `DirectLinkExtension` | 提供 DirectLink 核心运行时功能和管理器接口，是 `DirectLinkExtensionEditor` 的基础。 |
| `ContentBrowserFrontEnd` | 提供内容浏览器前端过滤器扩展的基类 `UContentBrowserFrontEndFilterExtension`。 |
| `DatasmithImporter` | Datasmith 导入器的核心模块，提供资产转换和导入的基础功能。 |
| `DatasmithTranslator` | 定义 Datasmith 翻译器的接口，用于解析不同格式的源数据。 |

## 维护状态

### 近期更新

```
- c11db69b54bd [Datasmith] Modified DirectLinkExtension and ExternalSource modules to be runtime
```
*解读：最近一次提交将 `DirectLinkExtension` 和 `ExternalSource` 模块的类型从 Editor 改为 Runtime，这表明 Epic 正在调整模块结构，使其能在运行时（而不仅仅是编辑器中）被使用，可能为了支持打包后的应用程序或更灵活的部署。*

### 维护评价

-   **创建时间**：2019年10月，是一个相对成熟的插件。
-   **最近更新**：最近一次提交（基于提供的信息）是模块类型调整，属于架构优化，而非新功能或重大修复。这表明插件处于**稳定维护期**，核心功能已完善，更新主要集中在优化和兼容性上。
-   **活跃度**：作为 Epic Games 官方维护的企业级插件，其长期支持是有保障的。但日常更新频率可能不如社区插件高。
-   **已知限制**：需要手动启用（`EnabledByDefault: false`）。对源软件版本和 Datasmith 格式版本有兼容性要求。
-   **推荐使用**：**强烈推荐**。对于需要将专业设计数据（CAD/BIM/DCC）导入 UE 进行可视化、交互或数字孪生构建的项目，Datasmith Importer 是官方提供的最强大、最可靠的解决方案。尽管需要手动启用，但其带来的工作流效率提升是巨大的。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/DatasmithImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/DatasmithImporter/Source/DirectLinkTest) (DirectLinkTest 模块)