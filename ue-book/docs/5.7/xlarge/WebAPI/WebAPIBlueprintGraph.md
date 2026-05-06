# WebAPI

> Automated generation of web based APIs

| 属性 | 值 |
|---|---|
| 中文名 | WebAPI 蓝图图 |
| 分类 | Web |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（模板蓝图资产） |
| 模块 | `WebAPI` (Runtime), `WebAPIBlueprintGraph` (Runtime), `WebAPIEditor` (Runtime), `WebAPILiquidJS` (Runtime), `WebAPIOpenAPI` (Runtime), `PLUGIN_NAMEGenerated` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-11-15 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Web/WebAPI) | |

## 用途

WebAPI 插件通过自动从 OpenAPI 规范（或其他服务定义）生成 C++ 代码和蓝图节点，大幅简化了在 Unreal Engine 中集成 RESTful Web API 的过程。它允许开发者以声明式的方式定义 API 调用，并在蓝图中以异步操作（Latent Action 或 Callback）的形式直接使用，无需手动编写 HTTP 请求、JSON 解析等底层逻辑。

该插件特别适合需要频繁与后端服务交互的项目，如多人游戏的后台、实时数据仪表盘、Web 管理界面等。

## 使用场景

- 你正在开发一个需要从外部 REST API 获取数据（如排行榜、用户信息、天气数据）的客户端应用。
- 你的团队希望使用 **OpenAPI 规范** 来定义与后端服务的接口，并希望自动化生成对应的 UE 代码。
- 你希望让**蓝图设计师**能够独立处理 API 调用，而无需 C++ 程序员介入网络层。
- 你需要在编辑器中进行 API 请求调试，利用插件提供的编辑器工具快速测试终端。

## 蓝图用法

WebAPI 插件在蓝图中主要通过 **WebAPI Operation** 节点（由 `WebAPIBlueprintGraph` 模块提供）来使用。该节点会自动根据生成的操作对象（`UWebAPIOperationObject` 子类）创建输入/输出引脚，并支持两种异步执行模式：**Latent Action**（延迟动作，带执行线）和 **Callback**（回调，绑定成功/失败事件）。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `WebAPI Operation` | 调用一个预定义的 WebAPI 操作。在蓝图右键菜单中按名称搜索添加。 | `UK2Node_WebAPIOperation` |

### 使用示例（蓝图描述）

假设你已通过 OpenAPI 规范生成了 `GetPlayerInfo` 操作对象。

1. 在蓝图事件图表中，右键输入 **“GetPlayerInfo”**，选择 **“WebAPI Operation”** 节点。
2. 节点上会出现输入引脚（如 `PlayerId`）和输出引脚（`Success` / `Error` 执行线，以及结果数据引脚 `PlayerInfo`）。
3. **Latent Action 模式**（默认）：连接 `Success` 执行线到后续逻辑，使用 `PlayerInfo` 结果。无需额外绑定委托。
4. **Callback 模式**：右键节点 → **“Set Async Type”** → 选择 **Callback**。此时节点会移除执行线，改为暴露两个委托引脚（`OnSuccess` 和 `OnError`），你需要将它们绑定到自定义事件。

## C++ 用法

### 头文件引入

```cpp
// 引入蓝图图模块核心头文件
#include "WebAPIBlueprintGraph.h"
// 引入操作节点
#include "K2Node_WebAPIOperation.h"
// 引入操作对象基类（位于 WebAPI 核心模块）
#include "WebAPIOperationObject.h"
```

### 基本用法

创建一个自定义 WebAPI 操作对象（通常由代码生成工具生成，也可手动创建）：

```cpp
// 假设你有一个名为 UMyGetUserOperation 的类，继承自 UWebAPIOperationObject
UCLASS()
class UMyGetUserOperation : public UWebAPIOperationObject
{
    GENERATED_BODY()

public:
    // 定义操作参数（输入）
    UPROPERTY(BlueprintReadWrite, Category = "Parameters")
    FString UserId;

    // 定义成功委托（输出）
    DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnSuccess, const FString&, UserName);
    UPROPERTY(BlueprintAssignable)
    FOnSuccess OnSuccess;

    // 定义错误委托
    DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnError, const FString&, ErrorMessage);
    UPROPERTY(BlueprintAssignable)
    FOnError OnError;

    // 实现操作逻辑
    virtual void Activate() override;
};
```

在蓝图中使用该操作时，`UK2Node_WebAPIOperation` 会自动识别 `OnSuccess` 和 `OnError` 委托，并生成对应执行引脚或委托绑定。

### 进阶用法

从测试用例中提取的节点编译扩展逻辑（路径：`Engine/Plugins/Experimental/Web/WebAPI/Source/WebAPIBlueprintGraph/Private/K2Node_WebAPIOperation.cpp`）：

```cpp
// 编译阶段：将蓝图节点展开为实际调用链
void UK2Node_WebAPIOperation::ExpandNode(FKismetCompilerContext& CompilerContext, UEdGraph* SourceGraph)
{
    // 1. 获取工厂函数（生成操作对象实例）
    UFunction* FactoryFunc = GetFactoryFunction();
    
    // 2. 创建中间调用节点
    UK2Node_CallFunction* CallFactoryNode = CompilerContext.SpawnIntermediateNode<UK2Node_CallFunction>(this, SourceGraph);
    CallFactoryNode->SetFromFunction(FactoryFunc);
    CallFactoryNode->AllocateDefaultPins();
    
    // 3. 传递参数引脚
    // ...（详细引脚映射逻辑）
    
    // 4. 处理成功/失败委托
    if (AsyncType == EWebAPIOperationAsyncType::LatentAction)
    {
        // 创建 Latent Action 代理
        // ...
    }
    else // Callback
    {
        // 创建回调绑定节点
        // ...
    }
}
```

## Demo 示例

由于插件依赖自动生成的代码，以下提供一个最简单的**手动创建操作对象**并在 C++ 中调用的概念性示例（需要包含必要的 `#include`）。

**MyWebAPIOperation.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "WebAPIOperationObject.h"
#include "MyWebAPIOperation.generated.h"

DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FMyAPISuccess, const FString&, Result);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FMyAPIError, const FString&, Error);

UCLASS()
class UMyWebAPIOperation : public UWebAPIOperationObject
{
    GENERATED_BODY()

public:
    UPROPERTY(BlueprintReadWrite, Category="MyAPI")
    FString RequestEndpoint;

    UPROPERTY(BlueprintAssignable)
    FMyAPISuccess OnSuccess;

    UPROPERTY(BlueprintAssignable)
    FMyAPIError OnError;

    virtual void Activate() override
    {
        // 模拟网络请求
        if (RequestEndpoint.IsEmpty())
        {
            OnError.Broadcast("Empty endpoint");
            return;
        }
        // 实际应使用 HTTP 模块
        FString FakeResult = FString::Printf(TEXT("Success from %s"), *RequestEndpoint);
        OnSuccess.Broadcast(FakeResult);
    }

    static UMyWebAPIOperation* CreateMyOperation(const FString& Endpoint)
    {
        UMyWebAPIOperation* Op = NewObject<UMyWebAPIOperation>();
        Op->RequestEndpoint = Endpoint;
        return Op;
    }
};
```

**蓝图调用**：创建一个 `WebAPI Operation` 节点并指定 `UMyWebAPIOperation` 作为其操作类（通过生成工具的注册或手动在 `FBlueprintActionDatabaseRegistrar` 中注册）。

## 模块依赖

仅列出该插件独特的依赖项（已省略标准 Core/Engine/Slate 等模块）：

| 模块 | 用途 |
|---|---|
| `WebAPI` | 核心运行时，定义操作对象基类 (`UWebAPIOperationObject`)、HTTP 请求管理 |
| `WebAPIEditor` | 编辑器支持，提供设置页面、操作对象注册等 |
| `WebAPIOpenAPI` | OpenAPI 规范解析与代码生成 |
| `WebAPILiquidJS` | LiquidJS 模板引擎，用于生成代码文本 |

`WebAPIBlueprintGraph` 模块额外依赖 `KismetCompiler` 和 `BlueprintGraph`（非独特，已省略）。

## 维护状态

### 近期更新

```
- 2025-07-31 399ed9f8  Make FWindowsPlatformProcess::CreateProc... | 引擎级修复，可能涉及 WebAPI 底层进程调用
- 2025-06-11 afdf8d75  Replace some usages of FORCEINLINE...    | 代码风格改善，非功能性更新
- 2024-11-22 36771d79  Updated uplugin descriptor files...      | 修正插件描述文件的 Beta/Experimental 标志
- 2024-11-20 e2fe1c9e  Fixed object properties using MustImplement... | 修复属性元数据，可能影响操作对象
- 2024-11-15 a2c3875d  Cleanup of FSlateFontInfo constructor...   | 无关的引擎清理
```

### 维护评价

- **创建时间**：2024-11-15（实验性插件）
- **更新频率**：自创建后约 8 个月仅有一次针对插件描述文件的更新，其余均为引擎级全局修复。
- **活跃度**：当前无专门的功能更新或 bug 修复记录，可能维护不够活跃。
- **稳定性**：标记为实验性（`IsExperimentalVersion = true`），API 可能在新版本中变化，不建议用于生产项目。
- **推荐使用**：仅用于原型验证或对前沿功能有需求的开发，注意备份自定义代码。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Web/WebAPI)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/WebAPI/)（如果存在，此处应替换为实际 URL，当前 .uplugin 中 `DocsURL` 为空）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Web/WebAPI/Source/WebAPIBlueprintGraph/Private/Tests)（假定路径，实际可能无独立测试目录）