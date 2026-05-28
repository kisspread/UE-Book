# DirectLink Extension

> Extension module for DirectLink, handling connection management, URI resolution, and automatic re-import.

| 属性 | 值 |
|---|---|
| 中文名 | DirectLink 扩展 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DirectLinkExtension` (Runtime), `DirectLinkExtensionEditor` (Runtime), `DirectLinkTest` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithImporter) | |

## 用途

`DirectLinkExtension` 插件并非独立的导入器，而是 `DatasmithImporter` 生态中负责 **管理与外部软件通过 DirectLink 协议进行实时通信** 的核心运行时模块。它解决了从 Blender、3ds Max、CAD 等设计软件到 Unreal Engine 之间的**实时、双向数据同步**问题。

DirectLink 是 Epic 开发的用于在应用程序间交换场景数据（如几何体、材质、光照）的协议。此插件的核心作用是：
1.  **连接管理**：维护一个 `DirectLink::FEndpoint`，负责发现和连接其他应用程序发布的 DirectLink 数据源。
2.  **外部源抽象**：将每个 DirectLink 数据源封装为 `FDirectLinkExternalSource` 对象，提供统一的接口来查询状态、获取数据哈希以及触发加载。
3.  **自动重导入**：监听外部源的数据变化，并可以配置为自动重新导入关联的资产，实现“设计即预览”的实时工作流。
4.  **URI 解析**：提供 `directlink://` 协议的 URI 解析能力，用于在系统内唯一标识一个 DirectLink 数据源。

简单来说，如果你的工作流需要在外部设计软件中修改模型或材质，并立即在 Unreal 中看到更新，那么此模块就是底层支撑的关键技术。

## 使用场景

- 你在 Blender 或 3ds Max 中持续迭代一个产品模型，希望 Unreal 中的关卡或影片能实时反映模型的更改 → 启用此插件并配置资产的自动重导入。
- 你是一名建筑可视化艺术家，使用 CAD 软件进行设计，需要将建筑模型实时同步到 Unreal 中进行光照和材质调整 → 此插件与 Datasmith Importer 协同工作，处理实时数据流。
- 你正在开发一个工业设计审查流程，需要在多个 DCC 软件之间同步复杂的装配体 → 利用 DirectLink 的数据交换能力。

## 蓝图用法

插件提供了一个蓝图函数库，用于在蓝图中查询 DirectLink 状态。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetAvailableDirectLinkSourcesUri` | 获取所有当前可用的 DirectLink 数据源的 URI 列表。 | `UDirectLinkExtensionBlueprintLibrary` |
| `ParseDirectLinkSourceUri` | 将一个 DirectLink URI 字符串解析为其组成部分（计算机名、端点名、可执行文件名、源名）。 | `UDirectLinkExtensionBlueprintLibrary` |

### 使用示例（蓝图描述）

1.  **查询可用源**：调用 `GetAvailableDirectLinkSourcesUri` 节点，返回一个字符串数组，其中每个元素都是一个类似 `directlink://ComputerName/EndpointName/ExecutableName/SourceName?SourceId=...` 的 URI。
2.  **解析 URI**：如果需要更细粒度的信息，将一个 URI 字符串传递给 `ParseDirectLinkSourceUri` 节点。输出引脚将分别提供解析后的各个部分。
3.  结合 **数据表** 或 **枚举**，你可以构建一个简单的 UI，让用户从列表中选择要连接的外部源，并触发 Datasmith 场景的重新导入。

## C++ 用法

### 头文件引入

使用 DirectLink 管理器：
```cpp
#include "DirectLinkExtensionModule.h"
```
使用 DirectLink 外部源：
```cpp
#include "DirectLinkExternalSource.h"
```
使用 URI 解析器：
```cpp
#include "DirectLinkUriResolver.h"
```

### 基本用法

获取 DirectLink 管理器并连接到外部源：
```cpp
// 引自对 IDirectLinkManager 接口的典型使用模式
if (IDirectLinkExtensionModule::IsAvailable())
{
    // 获取全局管理器
    IDirectLinkManager& DirectLinkManager = IDirectLinkExtensionModule::Get().GetManager();

    // 获取可用的外部源列表
    TArray<TSharedRef<FDirectLinkExternalSource>> ExternalSources = DirectLinkManager.GetExternalSourceList();

    for (const TSharedRef<FDirectLinkExternalSource>& Source : ExternalSources)
    {
        if (Source->IsAvailable())
        {
            UE_LOG(LogTemp, Log, TEXT("DirectLink Source Found: %s"), *Source->GetSourceName());

            // 尝试打开数据流
            if (Source->OpenStream())
            {
                // 流已打开，可以监听数据更新或手动触发加载
                UE_LOG(LogTemp, Log, TEXT("Stream opened to: %s"), *Source->GetSourceName());
            }
        }
    }

    // 根据 URI 查找或创建特定的外部源
    FSourceUri DesiredUri = /* ... */;
    TSharedPtr<FDirectLinkExternalSource> SpecificSource = DirectLinkManager.GetOrCreateExternalSource(DesiredUri);
    if (SpecificSource.IsValid())
    {
        // 配置自动重导入（需要 UObject 资产）
        UObject* MyAsset = /* ... */;
        if (DirectLinkManager.SetAssetAutoReimport(MyAsset, true))
        {
            UE_LOG(LogTemp, Log, TEXT("Enabled auto-reimport for asset: %s"), *MyAsset->GetName());
        }
    }
}
```

### 进阶用法

自定义 DirectLink 外部源处理器：
```cpp
// 引自 FDirectLinkExternalSource 的派生和注册模式
class FMyCustomDirectLinkSource : public FDirectLinkExternalSource
{
public:
    explicit FMyCustomDirectLinkSource(const FSourceUri& InSourceUri)
        : FDirectLinkExternalSource(InSourceUri)
    {}

    // 实现连接请求处理逻辑
    virtual bool CanOpenNewConnection(const DirectLink::IConnectionRequestHandler::FSourceInformation& Source) override
    {
        // 自定义逻辑：例如，只接受来自特定应用程序的连接
        return Source.ExecutableName.Contains(TEXT("MySpecialApp"));
    }

protected:
    // 实现内部的场景接收器
    virtual TSharedPtr<DirectLink::ISceneReceiver> GetSceneReceiverInternal(
        const DirectLink::IConnectionRequestHandler::FSourceInformation& Source) override
    {
        // 返回你自定义的场景接收器，用于处理接收到的场景数据
        return MakeShared<FMyCustomSceneReceiver>();
    }
};

// 在模块启动时注册自定义的外部源类型
void FMyGameModule::StartupModule()
{
    if (IDirectLinkExtensionModule::IsAvailable())
    {
        IDirectLinkManager& Manager = IDirectLinkExtensionModule::Get().GetManager();
        Manager.RegisterDirectLinkExternalSource<FMyCustomDirectLinkSource>(FName("MyCustomSource"));
    }
}
```

## Demo 示例

一个最小化的示例，展示如何在游戏模块中监听 DirectLink 外部源。

**MyDirectLinkListener.h**
```cpp
#pragma once
#include "DirectLinkExternalSource.h"

class FMyDirectLinkListener
{
public:
    FMyDirectLinkListener();
    ~FMyDirectLinkListener();

private:
    void OnSnapshotUpdated(const TSharedRef<UE::DatasmithImporter::FDirectLinkExternalSource>& UpdatedSource);
    TSharedPtr<UE::DatasmithImporter::FDirectLinkExternalSource> CurrentSource;
    FDelegateHandle UpdateDelegateHandle;
};
```

**MyDirectLinkListener.cpp**
```cpp
#include "MyDirectLinkListener.h"
#include "DirectLinkExtensionModule.h"

FMyDirectLinkListener::FMyDirectLinkListener()
{
    if (IDirectLinkExtensionModule::IsAvailable())
    {
        IDirectLinkManager& Manager = IDirectLinkExtensionModule::Get().GetManager();
        TArray<TSharedRef<UE::DatasmithImporter::FDirectLinkExternalSource>> Sources = Manager.GetExternalSourceList();

        if (Sources.Num() > 0)
        {
            CurrentSource = Sources[0];
            if (CurrentSource->IsAvailable())
            {
                // 绑定数据更新委托
                // 注意：实际委托绑定可能需要根据 FDirectLinkExternalSource 的具体实现来调整
                UpdateDelegateHandle = /* ... */;
                CurrentSource->OpenStream();
                UE_LOG(LogTemp, Log, TEXT("Listener attached to DirectLink source: %s"), *CurrentSource->GetSourceName());
            }
        }
    }
}

FMyDirectLinkListener::~FMyDirectLinkListener()
{
    if (CurrentSource.IsValid())
    {
        // 解绑委托
        /* ... */
        CurrentSource->CloseStream();
        CurrentSource.Reset();
    }
}

void FMyDirectLinkListener::OnSnapshotUpdated(const TSharedRef<UE::DatasmithImporter::FDirectLinkExternalSource>& UpdatedSource)
{
    UE_LOG(LogTemp, Log, TEXT("Received update from: %s. New Hash: %s"),
        *UpdatedSource->GetSourceName(),
        *UpdatedSource->GetSourceHash().ToString());
    // 在此处处理场景更新，例如触发资产重新加载
}
```

## 模块依赖

此插件依赖于 DirectLink 核心库，这是它独特的依赖项。

| 模块 | 用途 |
|---|---|
| `DirectLink` | DirectLink 通信协议的核心库，提供端点（Endpoint）、场景交换（SceneExchange）等基础功能。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量截断为浮点数的编译器警告。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移部分日志宏到 UE_LOGF。 |
| 2026-04-02 | `50a24ff6` | Deprecated GetObjects*/ForEachObjectWithOuter functions that take bool bIncludeNestedObjects. Introd | 废弃了带有 `bIncludeNestedObjects` 参数的 `GetObjects` 系列函数。 |
| 2026-03-06 | `7b69892a` | clean up code changing texture properties with wrapping in PreEditChange/PostEditChange as required. | 清理纹理属性修改代码，确保符合编辑器事务（Transaction）规范。 |
| 2026-03-05 | `1adb9f68` | New material translator work: | 新的材质转换器相关工作（提交信息不完整，可能为进行中的工作）。 |

### 维护评价

`DirectLinkExtension` 插件创建于 2019 年，是 Epic 企业套件（Enterprise）中 Datasmith 解决方案的重要组成部分。从 Git 历史来看，**最近一次有实质功能意义的更新是 2026 年 3 月的新材质转换器工作**，后续的提交主要是代码维护、编译器警告修复和引擎内部 API 的适配（如日志宏迁移、废弃函数替换）。

**评价**：
- **状态**：**维护中**。虽然近期没有显著的新功能提交，但代码仍在持续更新以适配新引擎版本。
- **活跃度**：活跃度一般。作为成熟的企业级功能，其核心架构已稳定，更新集中在兼容性和维护性上。
- **推荐度**：**推荐使用**。如果你的项目需要与支持 DirectLink 的 DCC 软件（如 3ds Max, Maya, Blender 的 Datasmith 插件）进行实时数据同步，那么此模块是必选项。它与 `DatasmithImporter` 深度集成，是官方支持的实时数据交换解决方案。
- **注意事项**：该插件默认未启用（`EnabledByDefault=false`），需要在项目设置中手动启用。同时，它依赖于 `DirectLink` 底层库，该库可能在底层实现上有更复杂的依赖关系。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)