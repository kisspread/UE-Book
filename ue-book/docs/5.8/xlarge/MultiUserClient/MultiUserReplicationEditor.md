# Multi-User Editing

> Allow collaborative multi-users sessions in the Editor（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 多人编辑 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MultiUserClient` (Runtime), `MultiUserClientLibrary` (Runtime), `MultiUserReplicationEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-03-28 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/Concert/ConcertApp/MultiUserClient) | |

## 用途

MultiUserClient 是 Unreal Editor 中实现多用户实时协作编辑的核心插件。它不仅仅是一个会话启动器，而是提供了一整套框架，用于管理多个编辑器客户端之间的连接、状态同步和冲突解决。其核心价值在于：允许多个开发者（如关卡设计师、程序员、美术）同时在同一个 Unreal 项目中工作，实时看到彼此的修改，从而大幅提升团队协作效率，减少版本合并带来的麻烦。该插件是 Epic 的 Concert 协作系统的具体实现。

## 使用场景

-   **团队关卡设计**：多个设计师同时在一个巨大的开放世界关卡中工作，分别负责不同的区域，可以实时看到对方放置和修改的资产。
-   **程序与美术协同**：程序员在编写游戏逻辑时，美术可以直接在同一场景中调整材质或模型，程序能立即看到效果并进行调试。
-   **跨地点远程协作**：分布在不同地理位置的团队成员可以通过多用户会话共同编辑同一个项目，如同在同一间办公室。

## 蓝图用法

该插件主要为编辑器工具提供 C++ API，大部分核心功能不直接暴露为蓝图节点。与用户交互的界面（如会话管理窗口）是 Slate UI。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetClientContent` | 根据 `FConcertClientInfo` 获取匹配的客户端预设内容 | `UMultiUserReplicationSessionPreset` |
| `GetExactClientContent` | 根据 `FConcertClientInfo` 获取精确匹配的客户端预设内容 | `UMultiUserReplicationSessionPreset` |
| `ContainsClient` | 检查预设中是否包含匹配的客户端 | `UMultiUserReplicationSessionPreset` |
| `AddClientIfUnique` | 如果客户端唯一，则将其添加到预设中 | `UMultiUserReplicationSessionPreset` |
| `SetMuteContent` | 设置整个会话预设中的对象静音/取消静音状态 | `UMultiUserReplicationSessionPreset` |
| `GetMuteContent` | 获取整个会话预设中的对象静音/取消静音状态 | `UMultiUserReplicationSessionPreset` |
| `GenerateDescription` | 为 `UMultiUserReplicationStream` 生成可用于网络请求的描述 | `UMultiUserReplicationStream` |

### 使用示例（蓝图描述）

蓝图中主要操作的是 `UMultiUserReplicationSessionPreset` 和 `UMultiUserReplicationStream` 资产。你可以通过蓝图获取一个已保存的 `UMultiUserReplicationSessionPreset` 对象，然后调用 `GetClientPresets` 来遍历其中保存的所有客户端配置，或者使用 `GetMuteContent` 查看当前预设中哪些对象被标记为静音。这些操作通常用于自定义的会话配置管理工具中。

## C++ 用法

### 头文件引入

```cpp
#include "IMultiUserReplicationEditorModule.h"
#include "MultiUserReplicationStream.h"
#include "MultiUserReplicationSessionPreset.h"
```

### 基本用法

1.  **访问模块接口**：获取 `MultiUserReplicationEditor` 模块的单例接口。
    ```cpp
    // 检查模块是否可用
    if (UE::MultiUserReplicationEditor::IMultiUserReplicationEditorModule::IsAvailable())
    {
        // 获取模块接口
        UE::MultiUserReplicationEditor::IMultiUserReplicationEditorModule& ReplicationEditorModule = UE::MultiUserReplicationEditor::IMultiUserReplicationEditorModule::Get();
        // ... 使用模块功能
    }
    ```
    *来源: Internal/IMultiUserReplicationEditorModule.h*

2.  **操作复制流 (Replication Stream)**：创建或修改一个复制流，它定义了哪些对象参与同步。
    ```cpp
    // 创建一个新的复制流对象 (通常由资产工厂或编辑器创建)
    UMultiUserReplicationStream* MyStream = NewObject<UMultiUserReplicationStream>();

    // 设置其唯一ID
    MyStream->StreamId = FGuid::NewGuid();

    // 定义要复制的对象映射 (示例)
    FConcertObjectReplicationMap& ReplicationMap = MyStream->ReplicationMap;
    ReplicationMap.ReplicatedObjects.Add(MyActorA, FConcertReplication_ObjectReplicationSettings());
    ReplicationMap.ReplicatedObjects.Add(MyActorB, FConcertReplication_ObjectReplicationSettings());

    // 生成可用于网络请求的描述
    FConcertReplicationStream StreamDescription = MyStream->GenerateDescription();
    ```
    *来源: Internal/Assets/MultiUserReplicationStream.h*

### 进阶用法

使用**会话预设 (Session Preset)** 来快速配置和恢复复杂的多人会话。
```cpp
// 加载或创建一个会话预设资产
UMultiUserReplicationSessionPreset* SessionPreset = LoadObject<UMultiUserReplicationSessionPreset>(nullptr, TEXT("/Game/Presets/MyTeamPreset"));

// 准备客户端信息
FConcertClientInfo CurrentClientInfo;
CurrentClientInfo.DisplayName = TEXT("LevelDesigner_Alice");
CurrentClientInfo.DeviceName = FPlatformMisc::GetDeviceId();

// 检查并添加客户端预设
if (!SessionPreset->ContainsClient(CurrentClientInfo))
{
    // 创建新的客户端预设内容
    FMultiUserReplicationClientPreset NewClientPreset(CurrentClientInfo.DisplayName, CurrentClientInfo.DeviceName);
    // ... 配置 NewClientPreset 的 ReplicationMap, FrequencySettings 等

    // 添加到会话预设
    FMultiUserReplicationClientPreset* AddedPreset = SessionPreset->AddClientIfUnique(CurrentClientInfo, MyStream->StreamId);
    if (AddedPreset)
    {
        // 配置添加后的预设细节
    }
}

// 配置整个会话的静音内容 (例如，为了性能，暂不同步某些特效)
FMultiUserMuteSessionContent MuteContent;
MuteContent.MutedObjects.Add(FSoftObjectPath(TEXT("/Game/VFX/Explosion.EffectActor")), FConcertReplication_ObjectMuteSetting());
SessionPreset->SetMuteContent(MoveTemp(MuteContent));

// 保存预设资产 (需要在编辑器环境中)
// ...
```
*来源: Internal/Assets/MultiUserReplicationSessionPreset.h*

## Demo 示例

一个展示如何初始化模块并查询预设的最小示例。

**MyMultiUserHelper.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "MyMultiUserHelper.generated.h"

class UMultiUserReplicationSessionPreset;

UCLASS()
class UMyMultiUserHelper : public UGameInstanceSubsystem
{
	GENERATED_BODY()
public:
	virtual void Initialize(FSubsystemCollectionBase& Collection) override;

	UFUNCTION(BlueprintCallable, Category = "MultiUser")
	void CheckPresetClients(UMultiUserReplicationSessionPreset* Preset);
};
```

**MyMultiUserHelper.cpp**
```cpp
#include "MyMultiUserHelper.h"
#include "IMultiUserReplicationEditorModule.h"
#include "MultiUserReplicationSessionPreset.h"

void UMyMultiUserHelper::Initialize(FSubsystemCollectionBase& Collection)
{
	Super::Initialize(Collection);

	// 在子系统初始化时，检查多用户编辑模块
	if (UE::MultiUserReplicationEditor::IMultiUserReplicationEditorModule::IsAvailable())
	{
		UE_LOG(LogTemp, Log, TEXT("MultiUserReplicationEditor module is available!"));
	}
}

void UMyMultiUserHelper::CheckPresetClients(UMultiUserReplicationSessionPreset* Preset)
{
	if (!Preset) return;

	const TArray<FMultiUserReplicationClientPreset>& ClientPresets = Preset->GetClientPresets();
	for (const FMultiUserReplicationClientPreset& ClientPreset : ClientPresets)
	{
		UE_LOG(LogTemp, Log, TEXT("Preset contains client: %s (Device: %s)"),
			*ClientPreset.DisplayName, *ClientPreset.DeviceName);
	}

	if (ClientPresets.Num() == 0)
	{
		UE_LOG(LogTemp, Warning, TEXT("The preset has no saved client configurations."));
	}
}
```

## 模块依赖

从 `MultiUserReplicationEditor.Build.cs` 分析，该插件的模块依赖了 `Concert` 核心框架和 `Replication` 子系统。

| 模块 | 用途 |
|---|---|
| `Concert` | 核心协作框架，提供会话、客户端信息等基础类型。 |
| `ConcertClient` | 客户端实现，处理与服务器（或对等点）的网络通信。 |
| `ConcertSyncClient` | 同步客户端，负责具体的资产和操作同步逻辑。 |
| `ConcertTransport` | 协作系统的网络传输层。 |
| `ReplicationSubsystem` | 对象复制子系统，提供底层的对象属性复制功能。 |
| `ReplicationEditor` | 复制功能的编辑器扩展，提供UI和编辑逻辑。 |
| `AssetDefinition` | UE资产定义系统，用于注册 `UMultiUserReplicationSessionPreset` 资产类型。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `39d8e540` | IsObjectHierarchyReplicated lambda dereferences Object->IsA<AActor>() without a null check. IPropert | 修复了对象层级复制检查中的空指针解引用问题。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏迁移到更新的 UE_LOGF 宏。 |
| 2025-12-10 | `c4420deb` | Multi User: Fix crash in -game | 修复了在游戏模式（-game）下运行时的崩溃问题。 |
| 2025-12-10 | `fec01c4e` | Multi User: Register Multi User with the sandbox system. | 将多用户编辑功能注册到沙盒系统。 |
| 2025-11-26 | `025cea32` | Concert: Convert ConcertClient to use new FileSandbox API for package sandbox. | 将Concert客户端转换为使用新的文件沙盒API进行包沙盒操作。 |

### 维护评价

-   **活跃维护**：最近6个月内有功能性更新和重要Bug修复。
-   **核心组件**：作为UE编辑器协作功能的核心，长期受到Epic团队的关注和维护。
-   **实验性警告**：`.uplugin` 标记为 `IsBetaVersion: true`，且默认未启用 (`EnabledByDefault: false`)。这意味着该功能仍处于**测试阶段**，API和功能未来可能会有较大变动，不推荐在稳定的生产项目中深度依赖。
-   **推荐度**：非常适合用于**团队内部原型开发、协作关卡设计**等场景，可以显著提升效率。但在用于**正式的、长期维护的商业项目**时需谨慎，应充分评估其稳定性和版本兼容性。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/Concert/ConcertApp/MultiUserClient)
-   [官方文档]() (暂无)
-   [测试用例]() (相关测试通常位于 `Engine/Tests/` 目录下，例如针对 Concert 和 Replication 系统的测试)