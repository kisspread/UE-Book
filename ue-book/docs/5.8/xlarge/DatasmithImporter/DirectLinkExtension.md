# Datasmith Importer

> Importer for Datasmith files.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 数据导入桥 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DatasmithImporter` (Runtime), `DirectLinkExtension` (Runtime), `DatasmithTranslator` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithImporter) | |

## 用途

Datasmith Importer 并非一个简单的文件导入插件，而是 **Datasmith 实时连接生态系统** 的核心引擎。它解决的核心问题是：在 Unreal Engine 与外部设计应用程序（如 3ds Max, Revit, SketchUp 等）或文件格式之间，建立一个**高效、实时、双向的数据同步通道**。

其存在意义在于：
1.  **DirectLink 协议实现**：作为 DirectLink 连接的端点管理器，负责发现外部数据源（`FDirectLinkExternalSource`）、维护连接、以及处理场景数据的实时接收与更新。
2.  **自动化资产管线**：提供了强大的**自动重导入**功能。一旦外部源的数据发生更新，可以自动触发对应 UE 资产的重新导入，极大提升工作流效率。
3.  **统一的源访问层**：通过 `FSourceUri` 和 `IDirectLinkManager` 接口，为上层应用（如 Datasmith Importer UI）提供了一个统一的、与具体外部源格式无关的数据访问抽象层。

简而言之，它是连接你的设计软件和 Unreal Engine 实时项目的“数据桥梁”。

## 使用场景

-   **建筑设计与可视化**：你正在使用 Revit 进行建筑建模，并希望通过 DirectLink 在 UE 中实时查看材质、光照和模型的修改，无需反复手动导出和导入。
-   **工业设计评审**：你的团队使用 CATIA 或 SolidWorks 设计复杂机械，需要将装配体实时同步到 UE 中进行沉浸式评审或制作产品演示。
-   **自动化资产更新**：你的项目资产来源于一个由外部工具持续生成的文件，你希望 UE 中的资产能自动保持最新，无需手动干预。
-   **自定义资产管道集成**：你需要开发一个自定义的资产来源（如内部开发的工具或非标准格式），并希望将其无缝接入 Datasmith 的实时同步和自动重导入流程。

## 蓝图用法

本插件提供了一个蓝图函数库 `UDirectLinkExtensionBlueprintLibrary`，用于查询和管理 DirectLink 连接源。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Available Direct Link Sources Uri` | 获取当前所有可用的 DirectLink 源的 URI 字符串列表。 | `UDirectLinkExtensionBlueprintLibrary` |
| `Parse Direct Link Source Uri` | 解析一个 DirectLink 源 URI 字符串，提取出计算机名、端点名、可执行文件名、源名称等信息。 | `UDirectLinkExtensionBlueprintLibrary` |

### 使用示例（蓝图描述）

1.  **获取所有可用源**：在一个函数或图表中，拖拽 `Get Available Direct Link Sources Uri` 节点。它会返回一个 `TArray<FString>`，每个字符串都是一个可用源的 URI，格式如 `directlink://<ComputerName>/<ExecutableName>/<EndpointName>/<SourceName>?SourceId=<GUID>`。
2.  **解析特定源信息**：将上一步得到的某个 URI 字符串连接到 `Parse Direct Link Source Uri` 节点的输入引脚。该节点会将 URI 分解为各个组成部分，并输出到对应的输出引脚（`OutComputerName`, `OutExecutableName` 等），便于在蓝图中显示或进行条件判断。

## C++ 用法

C++ 用法的核心是通过 `IDirectLinkManager` 接口管理 DirectLink 连接和自定义外部源。

### 头文件引入

```cpp
#include "DirectLinkExtensionModule.h"
#include "IDirectLinkManager.h"
#include "DirectLinkExternalSource.h"
```

### 基本用法

**1. 获取 DirectLink 管理器单例**
```cpp
// 获取模块提供的 DirectLink 管理器
IDirectLinkManager& DirectLinkMgr = IDirectLinkExtensionModule::Get().GetManager();
```
*来源: Public/DirectLinkExtensionModule.h*

**2. 列出所有当前可用的 DirectLink 外部源**
```cpp
TArray<TSharedRef<FDirectLinkExternalSource>> AvailableSources = DirectLinkMgr.GetExternalSourceList();
for (const TSharedRef<FDirectLinkExternalSource>& Source : AvailableSources)
{
    UE_LOG(LogTemp, Log, TEXT("DirectLink Source: %s, Available: %s"),
        *Source->GetSourceName(),
        Source->IsAvailable() ? TEXT("True") : TEXT("False"));
}
```
*来源: Public/IDirectLinkManager.h, Public/DirectLinkExternalSource.h*

### 进阶用法

**1. 注册一个自定义的 FDirectLinkExternalSource 类型**
假设你有一个自定义的 `UMyCustomExternalSource` 类继承自 `FDirectLinkExternalSource`。你可以在你的模块启动时注册它，以便 DirectLink 管理器在发现兼容的源时自动实例化。
```cpp
// 在你的 IModuleInterface::StartupModule() 中
if (IDirectLinkExtensionModule::IsAvailable())
{
    IDirectLinkManager& DirectLinkMgr = IDirectLinkExtensionModule::Get().GetManager();
    DirectLinkMgr.RegisterDirectLinkExternalSource<UMyCustomExternalSource>(FName("MyCustomSource"));
}
```
*来源: Public/IDirectLinkManager.h*

**2. 设置资产自动重导入**
```cpp
// 假设你有一个通过 DirectLink 导入的 UStaticMesh 资产 (MyMesh)
UStaticMesh* MyMesh = /* ... */;
bool bEnableAutoReimport = true;

if (DirectLinkMgr.SetAssetAutoReimport(MyMesh, bEnableAutoReimport))
{
    UE_LOG(LogTemp, Log, TEXT("已为资产 %s 设置 DirectLink 自动重导入: %s"),
        *MyMesh->GetName(),
        bEnableAutoReimport ? TEXT("启用") : TEXT("禁用"));
}
```
*来源: Public/IDirectLinkManager.h*

## Demo 示例

一个最小化的 C++ 示例，展示如何注册一个自定义 ExternalSource 并监听其事件。

**MyCustomExternalSource.h**
```cpp
#pragma once

#include "DirectLinkExternalSource.h"

class UMyCustomExternalSource : public UE::DatasmithImporter::FDirectLinkExternalSource
{
public:
    explicit UMyCustomExternalSource(const UE::DatasmithImporter::FSourceUri& InSourceUri)
        : FDirectLinkExternalSource(InSourceUri)
    {
    }

protected:
    // 实现接口，决定是否接受来自此源的连接
    virtual bool CanOpenNewConnection(const DirectLink::IConnectionRequestHandler::FSourceInformation& Source) override
    {
        // 在此处添加你的连接接受逻辑，例如检查源名称或类型
        return true;
    }

    // 实现接口，返回用于接收场景数据的接收器
    virtual TSharedPtr<DirectLink::ISceneReceiver> GetSceneReceiverInternal(const DirectLink::IConnectionRequestHandler::FSourceInformation& Source) override
    {
        // 返回一个能处理你的数据格式的接收器（此处为示意，需实际实现）
        return nullptr; // TODO: 实现你的 FMySceneReceiver
    }
};
```

**MyModule.cpp**
```cpp
#include "Modules/ModuleManager.h"
#include "DirectLinkExtensionModule.h"

class FMyModule : public IModuleInterface
{
public:
    virtual void StartupModule() override
    {
        if (IDirectLinkExtensionModule::IsAvailable())
        {
            IDirectLinkManager& DirectLinkMgr = IDirectLinkExtensionModule::Get().GetManager();
            DirectLinkMgr.RegisterDirectLinkExternalSource<UMyCustomExternalSource>(FName("MyCustomSource"));
        }
    }

    virtual void ShutdownModule() override
    {
        if (IDirectLinkExtensionModule::IsAvailable())
        {
            IDirectLinkManager& DirectLinkMgr = IDirectLinkExtensionModule::Get().GetManager();
            DirectLinkMgr.UnregisterDirectLinkExternalSource(FName("MyCustomSource"));
        }
    }
};

IMPLEMENT_MODULE(FMyModule, MyModule)
```

## 模块依赖

你的模块需要依赖 `DirectLinkExtension` 模块来使用其管理器和外部源类型。

| 模块 | 用途 |
|---|---|
| `DirectLink` | DirectLink 通信协议的核心实现，提供端点、连接管理等底层功能。 |
| `DatasmithCore` | Datasmith 场景数据结构（`IDatasmithScene` 等）的核心定义，是数据交换的通用语言。 |
| `ExternalSource` | 定义了 `FExternalSource` 基类和 `FSourceUri`，是 `FDirectLinkExternalSource` 的父类。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了严格浮点模式下 double 常量截断为 float 的警告。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 日志调用迁移至更现代的 UE_LOGF。 |
| 2026-04-02 | `50a24ff6` | Deprecated GetObjects*/ForEachObjectWithOuter functions that take bool bIncludeNestedObjects. Introduced... | 弃用了使用 `bIncludeNestedObjects` 参数的旧版对象遍历函数，并引入了新的替代方法。 |
| 2026-03-06 | `7b69892a` | clean up code changing texture properties with wrapping in PreEditChange/PostEditChange as required. | 清理了修改纹理属性的代码，确保在编辑器更改前后正确调用 Pre/PostEditChange。 |
| 2026-03-05 | `1adb9f68` | New material translator work: | 新材质转换器的开发工作：（提示正在进行新功能开发）。 |

### 维护评价

**积极维护中**。该插件创建于2019年，属于企业级功能。从最近的提交记录看（截至2026年），它仍在被**积极维护和更新**。近期的工作集中在**代码现代化**（迁移日志系统、清理废弃API）和**稳定性/规范性修复**（浮点精度、编辑器事件），表明团队正在对代码进行技术债清理。2026年3月的提交暗示可能有新的核心功能（材质转换器）正在开发。这是一个成熟且仍在迭代的项目，**推荐使用**，尤其是对于有跨软件实时同步需求的工作流。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)