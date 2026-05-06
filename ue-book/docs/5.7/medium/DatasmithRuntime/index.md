# Datasmith Runtime

> （插件描述为空）

| 属性 | 值 |
|---|---|
| 中文名 | Datasmith 运行时 |
| 分类 | Other |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `DatasmithRuntime` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-05-01 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Enterprise/DatasmithRuntime) | |

## 用途

**Datasmith Runtime** 是一个实验性插件，允许在**运行时**（Runtime）加载、渲染和实时更新 Datasmith 场景，而无需依赖 Unreal Editor。它通过集成 Datasmith 翻译器和 DirectLink 协议，能够在游戏或应用中直接导入并显示 3D 场景（如 CAD、BIM 等工业数据），并支持增量更新。

该插件解决了传统 Datasmith 工作流只能在编辑器内导入的限制，适用于需要动态加载外部 3D 数据的非编辑器环境（如可视化应用、数字孪生、实时协同等）。

核心机制：
- 使用 `ADatasmithRuntimeActor` 作为关卡内的场景容器
- 通过 `UDatasmithRuntimeLibrary` 蓝图函数库触发文件导入
- 通过 `UDirectLinkProxy` 管理 DirectLink 连接，实时接收数据更新

## 使用场景

- 在**游戏或独立应用**中运行时加载 CAD/FBX/glTF 等模型文件
- 构建**数字孪生**应用，实时接收来自设计软件的 DirectLink 数据流
- 实现**多人协同编辑器**，在不重启应用的情况下增量更新场景内容
- 在**运行时动态替换**或混合不同来源的 3D 资源

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `LoadFile` | 通过 Datasmith 翻译器加载指定文件到 RuntimeActor | `UDatasmithRuntimeLibrary` |
| `GetDirectLinkProxy` | 获取全局 DirectLink 代理对象 | `UDatasmithRuntimeLibrary` |
| `GetEndPointName` | 返回当前 DirectLink 端点名称 | `UDirectLinkProxy` |
| `GetListOfSources` | 获取 DirectLink 网络中的可用源列表 | `UDirectLinkProxy` |
| `OnDirectLinkChange` | 事件：DirectLink 网络拓扑或数据发生变更时触发 | `UDirectLinkProxy` |

### 使用示例

1. **加载文件到关卡**
   - 在关卡中放置 `ADatasmithRuntimeActor`（蓝图中引用为 `DatasmithRuntimeActor` 变量）
   - 调用 `LoadFile (DatasmithRuntimeActor, FilePath)`，传入文件路径
   - 等待导入完成（可通过定时器或异步回调检查状态）

2. **接收 DirectLink 实时数据**
   - 获取 `DirectLinkProxy` 对象
   - 绑定 `OnDirectLinkChange` 事件
   - 调用 `GetListOfSources` 获取可用源，选择后通过 `OpenConnection` 连接
   - 当源端发布更新时，`OnDirectLinkChange` 触发，场景自动增量更新

## C++ 用法

### 头文件引入

```cpp
#include "DatasmithRuntime.h"
#include "DatasmithRuntimeBlueprintLibrary.h"
#include "DirectLink/DatasmithSceneReceiver.h"
```

### 基本用法

```cpp
// 在游戏模块启动时获取对 ADatasmithRuntimeActor 的引用
// 通常通过 SpawnActor 或在关卡中放置后获取

// 从文件加载场景
ADatasmithRuntimeActor* RuntimeActor = ...; // 从世界获取或创建
FString FilePath = TEXT("/Game/MyScene.fbx");
bool bSuccess = UDatasmithRuntimeLibrary::LoadFile(RuntimeActor, FilePath);
```

### DirectLink 连接

```cpp
// 获取 DirectLink 代理
UDirectLinkProxy* DirectLinkProxy = DatasmithRuntime::GetDirectLinkProxy();

// 获取端点名称
FString EndPointName = DirectLinkProxy->GetEndPointName();

// 获取源列表
TArray<FDatasmithRuntimeSourceInfo> Sources = DirectLinkProxy->GetListOfSources();

// 绑定变化事件
DirectLinkProxy->OnDirectLinkChange.AddDynamic(this, &AMyActor::OnDirectLinkChange);

// 连接到指定源（假设源索引 0 为 desired）
if (Sources.Num() > 0)
{
    // 内部通过 FDestinationProxy::OpenConnection 实现
    // 实际调用需通过内部逻辑，蓝图公开了 GetListOfSources 但没有直接连接函数
    // 可通过 ADatasmithRuntimeActor 的接口（C++ 内调用）
}
```

### 进阶用法

结合 `FUpdateContext` 结构体，可以自定义对场景增量更新的处理（高级用法，需继承 `ISceneChangeListener`）。

```cpp
// 实现场景变化监听器
class FMyChangeListener : public FDatasmithSceneReceiver::ISceneChangeListener
{
public:
    virtual void OnSceneChange(const FUpdateContext& UpdateContext) override
    {
        // 处理添加、更新、删除的元素
        for (auto& Element : UpdateContext.Additions)
        {
            // 创建或导入新元素
        }
    }
};

// 将监听器注册到 ADatasmithRuntimeActor 内部
// 通过 FDestinationProxy 构造时传入
```

## Demo 示例

### MinimalActor.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MinimalActor.generated.h"

class ADatasmithRuntimeActor;

UCLASS()
class AMinimalActor : public AActor
{
    GENERATED_UCLASS_BODY()

public:
    virtual void BeginPlay() override;

    UFUNCTION()
    void OnDatasmithSceneChanged();

private:
    UPROPERTY()
    ADatasmithRuntimeActor* RuntimeActor;

    UPROPERTY()
    class UDirectLinkProxy* DirectLinkProxy;
};
```

### MinimalActor.cpp

```cpp
#include "MinimalActor.h"
#include "DatasmithRuntimeBlueprintLibrary.h"
#include "DirectLink/DatasmithSceneReceiver.h"
#include "Engine/World.h"

AMinimalActor::AMinimalActor(const FObjectInitializer& ObjectInitializer)
    : Super(ObjectInitializer)
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMinimalActor::BeginPlay()
{
    Super::BeginPlay();

    // 1. 创建一个 DatasmithRuntimeActor 实例
    FActorSpawnParameters SpawnParams;
    SpawnParams.Name = TEXT("DatasmithSceneHost");
    RuntimeActor = GetWorld()->SpawnActor<ADatasmithRuntimeActor>(SpawnParams);

    // 2. 加载一个文件
    FString FilePath = TEXT("C:/Models/test.fbx");
    if (FPaths::FileExists(FilePath))
    {
        UDatasmithRuntimeLibrary::LoadFile(RuntimeActor, FilePath);
    }

    // 3. 连接 DirectLink
    DirectLinkProxy = DatasmithRuntime::GetDirectLinkProxy();
    if (DirectLinkProxy)
    {
        DirectLinkProxy->OnDirectLinkChange.AddDynamic(this, &AMinimalActor::OnDatasmithSceneChanged);
        // 可选择自动连接最近的源
        for (auto& Src : DirectLinkProxy->GetListOfSources())
        {
            // 实际连接需要通过 FDestinationProxy，这里示意
            // RuntimeActor 内部维护了 FDestinationProxy，可调用 OpenConnection
        }
    }
}

void AMinimalActor::OnDatasmithSceneChanged()
{
    // DirectLink 数据更新时自动刷新场景
    UE_LOG(LogTemp, Log, TEXT("Scene updated via DirectLink"));
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `DatasmithImporter` | 提供 Datasmith 翻译器、导入选项和材质选择器 |
| `UdpMessaging` | 提供 DirectLink 网络通信所需的 UDP 消息传输 |
| `DirectLink` | 直接链接协议，用于实时场景同步 |

> 此外，`DatasmithRuntime` 通过 `DatasmithImporter` 间接依赖 `DatasmithCore`、`DatasmithTranslator` 等模块，但无需显式添加到使用者的 `Build.cs`。

## 维护状态

### 近期更新

从 git 日志中提取的最近提交：

- 2025-09-12 `32c74391` — 添加缺失的头文件。
- 2025-07-14 `8c4cad91` — StaticMesh 的 WITH_EDITORONLY_DATA 属性改为访问器模式。
- 2024-12-11 `03c93506` — 颜色函数添加 `[[nodiscard]]` 属性。
- 2024-06-17 `276d09f6` — 移除代码中所有简单的 `REN_ForceNoResetLoaders` 用法。
- 2024-05-01 `1dc22b36` — 骨架网格体修复：核对无效法线。

### 维护评价

- **创建时间**：2024-05-01，约 2 年前。
- **更新频率**：近 1 年内有 2 次实质性提交（2025 年），处于活跃维护阶段。
- **内容**：更新多为编译修复、属性调整，未引入重大功能变化，但仍保持与引擎内部 API 变更同步。
- **实验性**：标记为 Beta，但已在多种工程场景中使用。
- **推荐度**：适合需要运行时导入 Datasmith 场景的用户，功能基本稳定，但需注意实验性标签。建议关注后续官方正式发布。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Enterprise/DatasmithRuntime)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/datasmith-runtime-plugin/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Enterprise/DatasmithRuntime/Tests)（仅测试相关目录，如存在）