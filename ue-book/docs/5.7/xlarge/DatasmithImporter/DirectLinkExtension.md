# Datasmith Importer

> Importer for Datasmith files.

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

Datasmith Importer 插件的核心功能是**将来自各种 CAD、BIM 和 DCC 软件（如 Revit, 3ds Max, SketchUp, SolidWorks 等）的复杂设计数据，通过 Datasmith 格式高效、高保真地导入到 Unreal Engine 中**。它不仅仅是一个简单的文件导入器，更是一个**实时数据同步和协作的桥梁**。

其存在是为了解决工业设计、建筑可视化、产品展示等领域中，将专业设计软件创建的庞大、复杂且带有丰富元数据的模型，无缝集成到实时 3D 引擎中的痛点。它保留了原始设计中的层级结构、材质、灯光、元数据等信息，并支持通过 DirectLink 技术实现设计软件与 UE 之间的**实时双向同步**，极大地提升了设计评审和可视化的效率。

## 使用场景

- **建筑与施工 (AEC)**：建筑师使用 Revit 或 ArchiCAD 完成设计后，通过 Datasmith 将完整的 BIM 模型（包含墙体、门窗、MEP 系统等）导入 UE，用于创建沉浸式的建筑可视化或 VR 漫游。
- **产品设计与制造**：工业设计师在 SolidWorks 或 CATIA 中完成产品设计，通过 Datasmith 导入 UE 进行高质量的产品渲染、交互式配置或数字孪生构建。
- **实时设计评审**：设计师在 3ds Max 或 Cinema 4D 中调整场景，通过 DirectLink 实时同步到 UE 中，团队成员可以在 UE 的实时环境中即时看到更改并进行评审。
- **大型场景组装**：需要将来自不同软件（如 Revit 的建筑、3ds Max 的室内、Maya 的角色）的资产统一到一个 UE 项目中时，Datasmith 提供了标准化的导入和场景组织流程。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Available Direct Link Sources Uri` | 获取当前网络上所有可用的 DirectLink 数据源的 URI 列表。 | `UDirectLinkExtensionBlueprintLibrary` |
| `Parse Direct Link Source Uri` | 解析一个 DirectLink 源 URI 字符串，提取出计算机名、端点名、可执行文件名和源名称等组成部分。 | `UDirectLinkExtensionBlueprintLibrary` |

### 使用示例（蓝图描述）

1.  **发现可用源**：在蓝图中，调用 `Get Available Direct Link Sources Uri` 节点。该节点会返回一个字符串数组，每个字符串代表一个正在运行并广播 DirectLink 服务的外部应用程序（如 3ds Max, Revit）的 URI。
2.  **解析源信息**：将上一步获取到的某个 URI 字符串，连接到 `Parse Direct Link Source Uri` 节点的 `SourceUriString` 输入引脚。该节点会输出解析后的各个组成部分（`OutComputerName`, `OutEndpointName` 等），可用于在 UI 中显示或用于后续的连接逻辑。
3.  **建立连接**：通常，这些蓝图节点会与 Datasmith Content 或 Datasmith Scene Actor 的导入/更新逻辑结合使用，以选择特定的 DirectLink 源进行数据同步。

## C++ 用法

### 头文件引入

```cpp
#include "DirectLinkExtensionModule.h"
#include "DirectLinkExtensionBlueprintLibrary.h"
#include "DirectLinkExternalSource.h"
#include "IDirectLinkManager.h"
```

### 基本用法

以下示例展示了如何获取 DirectLink 管理器并查询当前可用的外部源。

```cpp
// 来源: DirectLinkExtensionModule.h
// 获取 DirectLink 扩展模块的单例
IDirectLinkExtensionModule& DirectLinkModule = IDirectLinkExtensionModule::Get();

// 获取 DirectLink 管理器
UE::DatasmithImporter::IDirectLinkManager& Manager = DirectLinkModule.GetManager();

// 获取当前所有已注册的 DirectLink 外部源
TArray<TSharedRef<UE::DatasmithImporter::FDirectLinkExternalSource>> ExternalSources = Manager.GetExternalSourceList();

for (const auto& Source : ExternalSources)
{
    UE_LOG(LogTemp, Log, TEXT("Found DirectLink Source: %s, Available: %s"),
        *Source->GetSourceName(),
        Source->IsAvailable() ? TEXT("Yes") : TEXT("No"));
}
```

### 进阶用法

以下示例展示了如何注册一个自定义的 `FDirectLinkExternalSource` 类型，并覆盖 URI 解析器。

```cpp
// 来源: IDirectLinkManager.h, DirectLinkExtensionModule.h
// 假设我们有一个自定义的外部源类型
class FMyCustomExternalSource : public UE::DatasmithImporter::FDirectLinkExternalSource
{
public:
    using FDirectLinkExternalSource::FDirectLinkExternalSource;
    // ... 实现必要的虚函数 ...
};

// 在模块启动时注册自定义类型
void FMyModule::StartupModule()
{
    if (IDirectLinkExtensionModule::IsAvailable())
    {
        IDirectLinkExtensionModule& DirectLinkModule = IDirectLinkExtensionModule::Get();
        UE::DatasmithImporter::IDirectLinkManager& Manager = DirectLinkModule.GetManager();
        
        // 注册自定义的外部源类型
        Manager.RegisterDirectLinkExternalSource<FMyCustomExternalSource>(FName("MyCustomSource"));
    }
}

// 覆盖默认的 URI 解析器
void FMyModule::OverrideResolver()
{
    if (IDirectLinkExtensionModule::IsAvailable())
    {
        IDirectLinkExtensionModule& DirectLinkModule = IDirectLinkExtensionModule::Get();
        
        // 创建并设置自定义的 URI 解析器
        TSharedRef<UE::DatasmithImporter::IUriResolver> MyResolver = MakeShared<FMyCustomUriResolver>();
        DirectLinkModule.OverwriteUriResolver(MyResolver);
    }
}
```

## Demo 示例

一个最小的示例，演示如何初始化 DirectLink 端点并解析一个 URI。

```cpp
// MyDirectLinkDemo.h
#pragma once
#include "CoreMinimal.h"

class FMyDirectLinkDemo
{
public:
    static void InitializeAndParseUri();
};
```

```cpp
// MyDirectLinkDemo.cpp
#include "MyDirectLinkDemo.h"
#include "DirectLinkExtensionModule.h"
#include "DirectLinkExtensionBlueprintLibrary.h"

void FMyDirectLinkDemo::InitializeAndParseUri()
{
    // 1. 确保 DirectLink 扩展模块可用
    if (!IDirectLinkExtensionModule::IsAvailable())
    {
        UE_LOG(LogTemp, Warning, TEXT("DirectLinkExtension module is not available."));
        return;
    }

    // 2. 获取 DirectLink 端点 (这会初始化核心连接)
    DirectLink::FEndpoint& Endpoint = IDirectLinkExtensionModule::GetEndpoint();
    UE_LOG(LogTemp, Log, TEXT("DirectLink Endpoint initialized."));

    // 3. 使用蓝图库函数获取可用源
    TArray<FString> AvailableSources = UDirectLinkExtensionBlueprintLibrary::GetAvailableDirectLinkSourcesUri();
    if (AvailableSources.Num() > 0)
    {
        const FString& FirstSourceUri = AvailableSources[0];
        UE_LOG(LogTemp, Log, TEXT("First available source URI: %s"), *FirstSourceUri);

        // 4. 解析这个 URI
        FString ComputerName, EndpointName, ExecutableName, SourceName;
        bool bSuccess = UDirectLinkExtensionBlueprintLibrary::ParseDirectLinkSourceUri(
            FirstSourceUri, ComputerName, EndpointName, ExecutableName, SourceName);

        if (bSuccess)
        {
            UE_LOG(LogTemp, Log, TEXT("Parsed URI - Computer: %s, Endpoint: %s, Executable: %s, Source: %s"),
                *ComputerName, *EndpointName, *ExecutableName, *SourceName);
        }
    }
    else
    {
        UE_LOG(LogTemp, Log, TEXT("No DirectLink sources currently available."));
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `DirectLink` | DirectLink 协议的核心运行时库，提供端点、连接、数据流等底层功能。 |
| `DatasmithCore` | Datasmith 的核心数据结构和场景表示，是导入和转换的基础。 |
| `ExternalSource` | 提供外部数据源 (`FExternalSource`) 的抽象基类和管理框架。 |

## 维护状态

### 近期更新

```
- 7495e4cc002d Change FTickableGameObjects that use the soon-to-be-deprecated IsAllowedToTick to instead use IsTickable if it is actually needed #jira UE-204963 #rb ben.hoffman
- fa90b399a485 Added includes for future change. This changelist only contains added #include and a couple of empty placeholder files
- 22e143492f7e DatasmithDirectLink - Fix crash on shutdown that could happen when receiving a DirectLink message while the engine is shutting down.
```

### 维护评价

Datasmith Importer 是一个**成熟且仍在维护中**的企业级插件。从创建时间（2019年）看已有约6年历史，属于“老古董”级别，但这通常意味着其功能稳定、经过大量项目验证。

近期的提交记录显示：
1.  **持续适配引擎更新**：如 `7495e4cc` 提交所示，插件在跟进引擎 API 的变更（如 `IsAllowedToTick` 的废弃），表明其与引擎主线保持同步。
2.  **稳定性修复**：`22e143492f7e` 修复了一个在引擎关闭时接收 DirectLink 消息可能导致的崩溃，这是对运行时稳定性的关键改进。
3.  **前瞻性准备**：`fa90b399a485` 为未来功能添加了头文件包含，说明有后续开发计划。

**综合评价**：该插件是 Unreal Engine 处理工业设计数据的核心组件，维护状态良好，更新频率适中（以修复和适配为主），**强烈推荐**在需要 CAD/BIM 数据导入和实时同步的项目中使用。由于其 `EnabledByDefault` 为 `false`，使用前需在插件管理器中手动启用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/DatasmithImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/DatasmithImporter/Source/DirectLinkTest)