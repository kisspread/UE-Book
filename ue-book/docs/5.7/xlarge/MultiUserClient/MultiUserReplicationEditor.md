# Multi-User Editing

> Allow collaborative multi-users sessions in the Editor（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MultiUserClient` (Runtime), `MultiUserClientLibrary` (Runtime), `MultiUserReplicationEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2019-06-10 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/Concert/ConcertApp/MultiUserClient) | |

## 用途

MultiUserClient 插件是 Unreal Engine 多用户编辑（Multi-User Editing）系统的核心客户端实现。它不仅仅是一个简单的网络同步工具，而是一个完整的协作框架，允许多个编辑器实例连接到同一个会话，并实时同步资产修改、编辑器操作和世界状态。

**核心解决的问题**：
1.  **实时协作**：允许多个开发者同时在同一个关卡或资产上工作，看到彼此的实时更改。
2.  **操作同步**：同步的不仅是数据，还包括编辑器操作（如移动Actor、修改属性），确保所有参与者看到一致的编辑器状态。
3.  **会话管理**：提供创建、加入、离开会话的完整生命周期管理。
4.  **复制控制**：提供精细的复制流（Replication Stream）和预设（Preset）系统，允许用户控制哪些对象、哪些属性需要被同步，以及同步的频率。

**为什么存在**：在大型项目开发中，美术、设计和程序经常需要协作搭建关卡或调试功能。传统的文件提交-合并流程效率低下且容易产生冲突。此插件通过实时同步编辑器状态，极大地提升了团队协作的效率和直观性。

## 使用场景

-   **关卡设计协作**：多个关卡设计师同时在一个大型开放世界关卡中放置植被、建筑和触发器，实时看到彼此的工作。
-   **程序与美术联调**：程序员在编辑器中调整一个角色的蓝图逻辑，美术师可以实时看到动画和特效的变化，并进行微调。
-   **QA与开发同步**：QA工程师可以连接到开发者的会话，实时复现和观察Bug，无需复杂的场景描述。
-   **教学与演示**：讲师可以创建一个会话，学生连接后可以看到讲师在编辑器中的每一步操作。

## 蓝图用法

本模块（MultiUserReplicationEditor）主要提供编辑器内的资产和预设管理功能，其蓝图节点通常用于构建自定义的多用户编辑器工具或自动化流程。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Generate Description` | 为当前复制流生成用于网络请求的描述信息。 | `UMultiUserReplicationStream` |
| `Make Replication Map Getter Attribute` | 创建一个指向此流复制映射的属性访问器，常用于绑定到UI。 | `UMultiUserReplicationStream` |
| `Get Client Content` | 根据客户端信息（显示名、设备名）从预设中获取对应的客户端复制设置。 | `UMultiUserReplicationSessionPreset` |
| `Add Client If Unique` | 向预设中添加一个唯一的客户端配置。 | `UMultiUserReplicationSessionPreset` |
| `Get Mute Content` | 获取预设中的静音（Mute）设置内容。 | `UMultiUserReplicationSessionPreset` |

### 使用示例（蓝图描述）

1.  **加载并应用一个会话预设**：
    *   使用 `Load Asset` 节点加载一个 `UMultiUserReplicationSessionPreset` 资产。
    *   调用 `Get Client Presets` 获取预设中保存的所有客户端配置数组。
    *   遍历数组，对每个 `FMultiUserReplicationClientPreset`，使用其 `ReplicationMap` 和 `FrequencySettings` 来配置当前会话的复制规则。
    *   使用 `Get Mute Content` 获取并应用静音设置。

2.  **创建一个新的复制流资产**：
    *   使用 `Create Asset` 节点创建一个 `UMultiUserReplicationStream` 对象。
    *   通过其 `ReplicationMap` 属性（`FConcertObjectReplicationMap` 类型）添加需要同步的对象和属性。
    *   调用 `Generate Description` 节点获取描述，用于后续的网络注册。

## C++ 用法

本模块的 C++ 接口主要用于深度集成或开发自定义的多用户编辑工具。

### 头文件引入

```cpp
#include "Assets/MultiUserReplicationStream.h"
#include "Assets/MultiUserReplicationSessionPreset.h"
#include "IMultiUserReplicationEditorModule.h"
```

### 基本用法

以下代码演示如何创建一个复制流并配置它。

```cpp
// 来源: 基于 MultiUserReplicationStream.h 的接口设计
#include "Assets/MultiUserReplicationStream.h"

void CreateAndConfigureReplicationStream()
{
    // 1. 创建一个新的复制流对象（通常在内存中，后续可保存为资产）
    UMultiUserReplicationStream* NewStream = NewObject<UMultiUserReplicationStream>();

    // 2. 配置复制映射：指定要同步的对象和属性
    FConcertObjectReplicationMap& RepMap = NewStream->ReplicationMap;
    
    // 示例：为某个Actor添加复制属性
    FConcertReplicatedObjectInfo ActorInfo;
    // ... 配置 ActorInfo 的属性列表 ...
    RepMap.ReplicatedObjects.Add(MyActor->GetFName(), ActorInfo);

    // 3. 生成网络描述，用于向服务器注册此流
    FConcertReplicationStream StreamDescription = NewStream->GenerateDescription();
    
    // 4. 使用 StreamDescription 进行网络操作...
}
```

### 进阶用法

结合会话预设，实现保存和加载完整的多用户复制配置。

```cpp
// 来源: 基于 MultiUserReplicationSessionPreset.h 的接口设计
#include "Assets/MultiUserReplicationSessionPreset.h"
#include "ConcertMessages.h" // for FConcertClientInfo

void SaveCurrentSessionToPreset(UMultiUserReplicationSessionPreset* PresetAsset)
{
    if (!PresetAsset) return;

    // 假设我们有一个当前活跃的复制流
    UMultiUserReplicationStream* CurrentStream = GetCurrentActiveStream();
    if (!CurrentStream) return;

    // 1. 构造客户端信息
    FConcertClientInfo ClientInfo;
    ClientInfo.DisplayName = TEXT("Designer_A");
    ClientInfo.DeviceName = FPlatformProcess::ComputerName();

    // 2. 将当前流的配置添加到预设中
    FMultiUserReplicationClientPreset* ClientPreset = PresetAsset->AddClientIfUnique(ClientInfo, CurrentStream->StreamId);
    if (ClientPreset)
    {
        ClientPreset->ReplicationMap = CurrentStream->ReplicationMap;
        // ClientPreset->FrequencySettings = ...; // 设置频率
    }

    // 3. 保存预设资产
    // ... 使用 FAssetEditorManager 或其他方法保存 PresetAsset ...
}
```

## Demo 示例

一个最小化的示例，展示如何创建一个 `UMultiUserReplicationStream` 对象并获取其描述。

**MyMultiUserTool.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Assets/MultiUserReplicationStream.h"

class FMyMultiUserTool
{
public:
    /** 创建一个示例复制流并打印其描述 */
    static void CreateSampleStreamAndDescribe();
};
```

**MyMultiUserTool.cpp**
```cpp
#include "MyMultiUserTool.h"
#include "UObject/UObjectGlobals.h"

void FMyMultiUserTool::CreateSampleStreamAndDescribe()
{
    // 创建一个临时的复制流对象
    UMultiUserReplicationStream* Stream = NewObject<UMultiUserReplicationStream>();
    
    // 简单配置：假设我们要同步一个名为 “MyActor” 的对象
    FConcertReplicatedObjectInfo ObjectInfo;
    // 这里可以进一步配置 ObjectInfo.Properties 来指定同步哪些属性
    Stream->ReplicationMap.ReplicatedObjects.Add(FName(TEXT("MyActor")), ObjectInfo);

    // 生成描述
    FConcertReplicationStream Description = Stream->GenerateDescription();
    
    // 输出描述信息（示例）
    UE_LOG(LogTemp, Log, TEXT("Generated Replication Stream Description:"));
    UE_LOG(LogTemp, Log, TEXT("  Stream ID: %s"), *Description.Identifier.ToString());
    UE_LOG(LogTemp, Log, TEXT("  Contains %d object(s)"), Description.BaseDescription.ReplicatedObjects.Num());
}
```

## 模块依赖

从 `MultiUserReplicationEditor.Build.cs` 分析，该模块依赖于 Concert 框架的核心组件。

| 模块 | 用途 |
|---|---|
| `Concert` | 多用户编辑的核心通信和同步框架。 |
| `ConcertClient` | 多用户编辑的客户端实现库。 |
| `ConcertShared` | Concert 框架的共享数据类型和工具。 |
| `Replication` | 提供底层的对象属性复制逻辑和数据结构（如 `FConcertObjectReplicationMap`）。 |

## 维护状态

### 近期更新

```
- 21dd6b7fd4ec Multi-User presets now associate replication settings by actor label.
- 0c8ba5e40bf5 Make Multi User replication preset independent from UMultiUserReplicationStream. Moved frequency settings out from UMultiUserReplicationStream because it was not being used.
- e274710b68b0 Make FReplicationClient use UMultiUserReplicationStream instead of UMultiUserReplicationClientContent. This separates the replication system to use UMultiUserReplicationStream while the presets can use UMultiUserReplicationClientContent, giving each class a single responsibility. This is in preparation for a change to what is saved in the presets.
```

### 维护评价

-   **活跃维护**：从最近的提交记录看，该模块仍在积极开发和重构中（例如，将预设与流解耦、改进预设的绑定逻辑）。这些是功能性的架构改进，而非简单的编译修复。
-   **实验性状态**：插件标记为 `IsBetaVersion: true` 且默认未启用 (`EnabledByDefault: false`)，表明 Epic 将其视为一个高级或实验性功能，API 和行为可能在未来版本中发生变化。
-   **推荐使用**：**推荐给需要深度多人协作的团队使用**。虽然处于 Beta 状态，但它是 Epic 官方提供的唯一原生多用户编辑解决方案，功能完整且持续更新。使用时应关注版本更新日志，以适应可能的 API 变更。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/Concert/ConcertApp/MultiUserClient)
-   [官方文档](https://docs.unrealengine.com/5.7/en-US/multi-user-editing-in-unreal-engine/) (UE5 官方文档链接)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/Concert/ConcertApp/MultiUserClient/Tests) (如果存在)