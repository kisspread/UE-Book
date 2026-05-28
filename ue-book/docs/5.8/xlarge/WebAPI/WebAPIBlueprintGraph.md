# WebAPI

> Automated generation of web based APIs（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | Web接口 |
| 分类 | Web |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、代码模板） |
| 模块 | `WebAPI` (Runtime), `WebAPIBlueprintGraph` (Runtime), `WebAPIEditor` (Runtime), `WebAPILiquidJS` (Runtime), `WebAPIOpenAPI` (Runtime), `PLUGIN_NAMEGenerated` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-07-11 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Web/WebAPI) | |

## 用途

WebAPI 插件旨在通过蓝图可视化编程，自动生成基于 REST 的 Web 服务端代码。它解决了在 UE 项目中手动编写和维护 API 接口、数据模型以及路由逻辑的繁琐问题。

该插件的核心存在意义是将 API 的开发流程**蓝图化**和**自动化**。开发者可以在蓝图中定义数据结构（如 USTRUCT）和操作（UFUNCTION），插件会利用模板（LiquidJS）和编译后端，自动生成包含模型、操作、路由的、可直接部署的 C++ 服务器代码或蓝图资产。这使得游戏后端服务、内部工具接口的开发更快速、更符合 UE 开发者的工作流。

## 使用场景

- **构建游戏微服务后端**：你需要为你的在线游戏快速创建一组内部 API，用于管理玩家数据、游戏配置等，而不希望从零开始搭建服务器框架。
- **开发编辑器工具的 Web 界面**：你正在编写一个复杂的 UnrealEd 插件，并希望通过浏览器访问其部分功能。
- **前后端分离架构的快速原型**：项目采用 UE 作为客户端，需要快速定义和验证与服务器端通信的接口。
- **自动化测试接口**：需要为自动化测试工具提供可控的游戏状态修改接口。

## 蓝图用法

WebAPI 在蓝图中主要通过特殊的 **K2 节点（蓝图节点）** 和**数据资产**进行交互，将 API 的定义过程集成到蓝图编辑器中。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `WebAPI Operation` (K2Node) | 核心操作节点。用于在蓝图中发起一个已定义的 API 调用，支持异步和委托两种模式。 | `UK2Node_WebAPIOperation` |
| `Set Async Type` | 设置操作节点的异步模式（Latent Action 或 Callback）。 | `UK2Node_WebAPIOperation` |
| `Success` / `Error` (Output Delegate) | 操作完成后的结果委托引脚，分别对应成功和失败。 | `UK2Node_WebAPIOperation` |
| `分支操作 (Branch on Operation)` | 一个条件节点，根据 API 操作的结果（成功/失败）执行不同的逻辑分支。 | (基于 `UK2Node_WebAPIOperation` 的上下文菜单) |

### 异步模式

在 `UK2Node_WebAPIOperation` 上，可以通过右键菜单或 `SetAsyncType` 函数切换两种异步处理模式：
1.  **Latent Action (潜行动作)**：默认模式。节点会像 `Delay` 节点一样，在时间线上阻塞执行，直到操作完成。适用于大多数简单流程。
2.  **Callback (委托回调)**：当操作在蓝图函数中被调用时（Latent Action 在函数内不可用），会自动切换到此模式。操作完成后，通过 `Success` 和 `Error` 输出委托执行后续逻辑。

### 使用示例（蓝图描述）

假设你已经通过 WebAPI 编辑器定义了一个名为 `GetPlayerStats` 的 API 操作。
1.  在蓝图事件图表中，右键搜索并添加 `GetPlayerStats` 操作节点。
2.  **输入引脚**：连接 `PlayerID` 等必要的输入参数。
3.  **执行引脚**：从 `BeginPlay` 或其他事件连出执行线到操作的输入执行引脚。
4.  **输出处理**：
    - **Latent 模式**：从操作节点的 `Then` 引脚连出执行线，接下来连接 `PrintString` 节点，此时 `Response` 引脚已包含返回的数据。
    - **Callback 模式**：将 `Success` 委托引脚连接到一个自定义事件或函数，该函数包含处理成功响应的逻辑；将 `Error` 委托引脚连接到处理错误的函数。
5.  **分支**：也可以右键操作节点，选择 `Branch on Operation`，自动生成一个分支节点，分别连接成功和失败的后续逻辑。

## C++ 用法

WebAPI 的底层逻辑由 C++ 实现，蓝图节点是其上层封装。高级用户或需要深度定制的开发者可以直接使用其 C++ API。

### 头文件引入

```cpp
#include "WebAPIOperationObject.h"
#include "WebAPIBlueprintGraph.h"
```

### 基本用法

以下代码片段展示了如何以编程方式与 WebAPI 操作交互（概念参考自 `UK2Node_WebAPIOperation` 的设计）。

```cpp
// 假设你有一个已生成的 UWebAPIOperationObject 子类 UGetPlayerStatsOperation
UGetPlayerStatsOperation* Operation = NewObject<UGetPlayerStatsOperation>();

// 绑定成功和失败的回调
Operation->SuccessDelegate.AddDynamic(this, &UMyClass::OnStatsSuccess);
Operation->ErrorDelegate.AddDynamic(this, &UMyClass::OnStatsError);

// 设置参数并执行
Operation->SetPlayerID(PlayerID);
Operation->Execute(); // 触发异步网络请求

// 在回调中处理结果
void UMyClass::OnStatsSuccess(const FWebAPIResponse& Response)
{
    // 处理成功返回的数据
}

void UMyClass::OnStatsError(const FWebAPIError& Error)
{
    // 处理错误
}
```
*注：以上为基于源码结构的示意代码，展示了 `UK2Node_WebAPIOperation` 可能展开后的底层逻辑。*

### 进阶用法

深入 `WebAPIBlueprintGraph` 模块，可以了解蓝图节点是如何扩展和编译的。

```cpp
// 在蓝图编辑器中操作 WebAPI 节点的内部机制示例
#include "K2Node_WebAPIOperation.h"
#include "WebAPIBlueprintGraphUtilities.h"

// 1. 获取操作类的“成功”委托属性
const FMulticastDelegateProperty* SuccessProp = 
    UE::WebAPI::Operation::GetPositiveOutcomeDelegate<UGetPlayerStatsOperation>();

// 2. 在蓝图图表中查找或修改 WebAPI 操作节点
void ModifyWebAPINodeInGraph(UEdGraph* Graph)
{
    for (UEdGraphNode* Node : Graph->Nodes)
    {
        if (UK2Node_WebAPIOperation* WebAPINode = Cast<UK2Node_WebAPIOperation>(Node))
        {
            // 检查节点有效性
            if (WebAPINode->IsValid())
            {
                // 切换异步模式
                WebAPINode->SetAsyncType(EWebAPIOperationAsyncType::Callback);
                
                // 获取其请求参数引脚
                TArray<UEdGraphPin*> RequestPins = WebAPINode->GetRequestPins();
                // ... 对引脚进行操作
            }
        }
    }
}
```
*代码来源：基于 `Private/K2Node_WebAPIOperation.h` 和 `Private/WebAPIBlueprintGraphUtilities.h` 中的接口推断。*

## Demo 示例

以下是一个最小化的 C++ 示例，展示如何定义一个可被 WebAPI 插件识别并生成代码的“操作”类骨架。

**WebAPIDemoOperation.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "WebAPIOperationObject.h"
#include "WebAPIDemoOperation.generated.h"

// 1. 定义操作的输入数据结构
USTRUCT(BlueprintType)
struct FWebAPIDemoRequest
{
    GENERATED_BODY()
    
    UPROPERTY(BlueprintReadWrite, EditAnywhere)
    FString PlayerID;
};

// 2. 定义操作的输出数据结构
USTRUCT(BlueprintType)
struct FWebAPIDemoResponse
{
    GENERATED_BODY()

    UPROPERTY(BlueprintReadOnly)
    int32 Score;

    UPROPERTY(BlueprintReadOnly)
    FString Rank;
};

// 3. 定义操作类，继承自 UWebAPIOperationObject
UCLASS(BlueprintType)
class UWebAPIDemoOperation : public UWebAPIOperationObject
{
    GENERATED_BODY()

public:
    // 操作的友好名称，用于生成代码和蓝图节点名
    virtual FName GetOperationName() const override { return TEXT("GetDemoData"); }
    
    // 定义成功和失败的委托
    DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnDemoSuccess, const FWebAPIDemoResponse&, Response);
    DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnDemoError, const FWebAPIError&, Error);
    
    UPROPERTY(BlueprintAssignable)
    FOnDemoSuccess SuccessDelegate;
    
    UPROPERTY(BlueprintAssignable)
    FOnDemoError ErrorDelegate;
    
    // 存储输入参数
    UPROPERTY(BlueprintReadWrite)
    FWebAPIDemoRequest Request;
    
    // 执行操作的核心方法（通常由插件生成，此处为示意）
    UFUNCTION(BlueprintCallable)
    void Execute();
};
```

**WebAPIDemoOperation.cpp**
```cpp
#include "WebAPIDemoOperation.h"

void UWebAPIDemoOperation::Execute()
{
    // 模拟一个异步网络请求
    AsyncTask(ENamedThreads::AnyBackgroundThreadNormalTask, [this]()
    {
        // 模拟网络延迟
        FPlatformProcess::Sleep(2.0f);
        
        // 切回游戏线程广播结果
        AsyncTask(ENamedThreads::GameThread, [this]()
        {
            if (!Request.PlayerID.IsEmpty())
            {
                FWebAPIDemoResponse Response;
                Response.Score = 100;
                Response.Rank = TEXT("Gold");
                SuccessDelegate.Broadcast(Response);
            }
            else
            {
                FWebAPIError Error;
                Error.ErrorMessage = TEXT("Invalid PlayerID");
                ErrorDelegate.Broadcast(Error);
            }
        });
    });
}
```

## 模块依赖

在你的项目模块（`.Build.cs`）中使用 WebAPI 功能，可能需要添加以下依赖（具体取决于使用的深度）：

| 模块 | 用途 |
|---|---|
| `WebAPI` | 核心运行时模块，包含操作对象、网络通信等基础功能。 |
| `WebAPILiquidJS` | 提供 Liquid 模板引擎支持，用于代码生成。如果你的插件需要自定义生成模板，需要依赖此模块。 |
| `WebAPIBlueprintGraph` | 提供蓝图节点支持。如果你的插件需要向 WebAPI 蓝图节点添加自定义行为或扩展，需要依赖此模块。 |
| `WebAPIOpenAPI` | 可能用于支持 OpenAPI (Swagger) 规范的导入导出。 |

**注意**：`WebAPIEditor` 模块为编辑器专用，仅在编辑器环境下需要。在你的游戏运行时模块中不应依赖它。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下，双精度常量被截断为浮点数的警告。 |
| 2026-04-30 | `361e0c84` | Refactored FJsonObject to support both FString and UE::FSharedString | 重构 FJsonObject 以同时支持 FString 和 UE::FSharedString，优化内存使用。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧的 UE_LOG 日志宏迁移到新的 UE_LOGF 宏。 |
| 2026-03-02 | `9758fa58` | FORT-984709 - Remove string duplication in FJsonObject to free memory | 移除 FJsonObject 中的字符串重复，释放内存。 |
| 2026-02-18 | `516817d0` | PR #13954: fix(deps): on-headers is vulnerable to http response header manipulation (and other vulne | 更新依赖库以修复安全漏洞。 |

### 维护评价

- **创建时间**：插件于2022年7月创建，相对较新。
- **近期活跃度**：最近一次更新在2026年5月，说明插件仍处于**活跃维护**状态。近期的提交主要集中在代码质量优化（重构、警告修复、内存优化）和依赖安全更新，而非重大新功能。
- **稳定性**：作为 `Experimental` 插件且默认禁用，表明它可能还未达到生产就绪的稳定性，API 和功能未来可能会发生变化。
- **推荐使用**：适合进行技术调研、原型开发或学习 UE 插件架构。若用于生产项目，需评估其稳定性并做好应对 API 变更的准备。建议密切关注其官方状态变化（如从 Experimental 移除或标记为废弃）。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Web/WebAPI)
- 官方文档：暂无 (`.uplugin` 中 `DocsURL` 为空)