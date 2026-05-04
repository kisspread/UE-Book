# Unreal MCP

> Anthropic MCP (Model Context Protocol) server implementation for Unreal Engine.

| 属性 | 值 |
|---|---|
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ModelContextProtocol` (Runtime), `ModelContextProtocolEditor` (Runtime), `ModelContextProtocolEditorTests` (Runtime), `ModelContextProtocolEngine` (Runtime), `ModelContextProtocolEngineTests` (Runtime), `ModelContextProtocolTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-18 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ModelContextProtocol) | |

## 用途

ModelContextProtocol 插件实现了 Anthropic 的 MCP（Model Context Protocol）服务器，使 Unreal Engine 能够作为 MCP 服务器被 AI 模型（如 Claude）直接调用。

**核心解决的问题**：AI 助手无法直接操作 Unreal Engine。通过 MCP 协议，外部 AI 客户端可以发现并调用引擎中暴露的工具函数，实现 AI 驱动的自动化工作流——例如让 AI 帮你生成关卡内容、调用蓝图函数、查询引擎状态等。

**架构设计**：
- **ToolsetRegistry 系统**：通过 `UToolsetDefinition` 基类注册工具集，开发者在子类中标记 `UFUNCTION(meta = (AICallable))` 即可将函数暴露给 AI
- **MCP Server**：实现标准 MCP 协议，接受外部 AI 客户端的 JSON-RPC 请求
- **分层模块**：核心协议层（ModelContextProtocol）、编辑器集成层（ModelContextProtocolEditor）、引擎集成层（ModelContextProtocolEngine），各层独立可测试

## 使用场景

- 你在使用 Claude 等 AI 助手开发游戏 → 通过 MCP 让 AI 直接操作引擎，如放置 Actor、修改材质参数
- 你需要 AI 辅助关卡设计 → 暴露关卡操作函数，让 AI 根据描述生成场景
- 你想构建 AI 驱动的自动化测试 → AI 通过 MCP 调用引擎功能并验证结果
- 你在开发 AI Agent 工具链 → 将 UE 作为可被 AI 调用的工具节点

## 蓝图用法

本插件的核心 API 通过 C++ 元数据标记暴露，蓝图中主要通过创建 `UToolsetDefinition` 子类来注册 AI 可调用的工具。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Greet` | 通过姓名打招呼（测试用示例） | `UMockToolsetDefinition` |
| `Add` | 两数相加（测试用示例） | `UMockToolsetDefinition` |

### 使用示例（蓝图描述）

本插件主要面向 C++ 开发者。要暴露函数给 AI：

1. 创建 `UToolsetDefinition` 的子类
2. 在需要暴露的函数上添加 `UFUNCTION(meta = (AICallable))` 标记
3. 函数必须是 `static` 的
4. MCP 服务器启动后，AI 客户端即可发现并调用这些函数

## C++ 用法

### 头文件引入

```cpp
#include "ToolsetRegistry/ToolsetDefinition.h"
```

### 基本用法

创建一个工具集定义类，将函数暴露给 MCP AI 客户端：

```cpp
// MyToolset.h
#pragma once

#include "ToolsetRegistry/ToolsetDefinition.h"
#include "MyToolset.generated.h"

UCLASS()
class UMyToolset : public UToolsetDefinition
{
    GENERATED_BODY()

public:
    /** 查询场景中所有 Actor 的数量 */
    UFUNCTION(meta = (AICallable))
    static int32 GetActorCount();

    /** 根据名称查找 Actor 的位置 */
    UFUNCTION(meta = (AICallable))
    static FVector FindActorLocation(const FString& ActorName);
};
```

```cpp
// MyToolset.cpp
#include "MyToolset.h"

int32 UMyToolset::GetActorCount()
{
    UWorld* World = GEngine->GetWorldContexts()[0].World();
    TArray<AActor*> AllActors;
    UGameplayStatics::GetAllActorsOfClass(World, AActor::StaticClass(), AllActors);
    return AllActors.Num();
}

FVector UMyToolset::FindActorLocation(const FString& ActorName)
{
    UWorld* World = GEngine->GetWorldContexts()[0].World();
    TArray<AActor*> AllActors;
    UGameplayStatics::GetAllActorsOfClass(World, AActor::StaticClass(), AllActors);
    for (AActor* Actor : AllActors)
    {
        if (Actor->GetName() == ActorName)
        {
            return Actor->GetActorLocation();
        }
    }
    return FVector::ZeroVector;
}
```

> 来源：`Private/Mocks/MockToolsetDefinition.h` 中的模式推断

### 进阶用法

`AICallable` 元标记支持基本类型（FString、int32、float）和 UE 类型（FVector 等）作为参数和返回值。函数必须是 `static` 的，因为 MCP 调用是无状态的远程过程调用。

## Demo 示例

### 完整的 AI 可调用工具集

```cpp
// AITools.h
#pragma once

#include "ToolsetRegistry/ToolsetDefinition.h"
#include "AITools.generated.h"

UCLASS()
class UAIDesignTools : public UToolsetDefinition
{
    GENERATED_BODY()

public:
    /** 在指定位置生成一个立方体 */
    UFUNCTION(meta = (AICallable))
    static bool SpawnCube(float X, float Y, float Z);

    /** 获取当前关卡名称 */
    UFUNCTION(meta = (AICallable))
    static FString GetCurrentLevelName();
};
```

```cpp
// AITools.cpp
#include "AITools.h"
#include "Engine/World.h"
#include "Engine/StaticMeshActor.h"
#include "Kismet/GameplayStatics.h"

bool UAIDesignTools::SpawnCube(float X, float Y, float Z)
{
    UWorld* World = GEngine->GetWorldContexts()[0].World();
    if (!World) return false;

    FActorSpawnParameters SpawnParams;
    AStaticMeshActor* Cube = World->SpawnActor<AStaticMeshActor>(
        FVector(X, Y, Z), FRotator::ZeroRotator, SpawnParams);
    return Cube != nullptr;
}

FString UAIDesignTools::GetCurrentLevelName()
{
    UWorld* World = GEngine->GetWorldContexts()[0].World();
    return World ? World->GetMapName() : TEXT("Unknown");
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ModelContextProtocol` | 核心 MCP 协议实现和 ToolsetRegistry |
| `ModelContextProtocolEditor` | 编辑器集成（MCP 服务器管理 UI 等） |
| `ModelContextProtocolEngine` | 引擎运行时集成 |

## 维护状态

### 近期更新

```
- 2026-04-18 初始提交，包含完整的 MCP 服务器实现、ToolsetRegistry 系统、编辑器/引擎集成及测试套件
```

### 维护评价

- **状态**：🆕 全新实验性插件
- **创建时间**：2026-04-18，极新
- **实验性标记**：`IsExperimentalVersion=true`，`EnabledByDefault=false`，需手动启用
- **模块化设计**：6 个模块（含 3 个测试模块），架构清晰，测试覆盖充分
- **推荐使用**：适合对 AI 驱动开发工作流感兴趣的开发者提前探索。作为实验性插件，API 可能发生重大变更。生产环境暂不建议依赖。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ModelContextProtocol)
- [MCP 协议规范](https://modelcontextprotocol.io/)