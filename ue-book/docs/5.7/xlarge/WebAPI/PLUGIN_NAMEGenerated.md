# WebAPI

> Automated generation of web based APIs

| 属性 | 值 |
|---|---|
| 中文名 | Web API 自动生成 |
| 分类 | Web |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、模板文件、编辑器工具） |
| 模块 | `WebAPI` (Runtime), `WebAPIBlueprintGraph` (Runtime), `WebAPIEditor` (Runtime), `WebAPILiquidJS` (Runtime), `WebAPIOpenAPI` (Runtime), `PLUGIN_NAMEGenerated` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-11-15 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Web/WebAPI) | |

## 用途

WebAPI 插件旨在解决 Unreal Engine 与外部 HTTP API 集成时手工编写绑定代码的痛点。它通过解析 OpenAPI 规范（Swagger）自动生成类型安全的 C++ 类和蓝图节点，并提供 LiquidJS 模板引擎支持自定义代码生成。开发者无需手动处理序列化、HTTP 请求构造与响应解析，只需定义一次 API 规范，即可获得完整的 UE 端调用库。

该插件包含多个子模块：
- **WebAPIOpenAPI**：解析 OpenAPI 3.0 规范（JSON/YAML），提取端点、参数、模型结构。
- **WebAPILiquidJS**：集成 LiquidJS 模板引擎，用于自定义生成代码的样式。
- **WebAPIEditor**：提供编辑器界面，用于导入规范、配置生成选项、预览生成结果。
- **WebAPIBlueprintGraph**：为蓝图系统提供自动生成的 HTTP 调用节点。
- **PLUGIN_NAMEGenerated**：模板占位模块，用于存放生成后的代码项目。

## 使用场景

- 你的游戏需要对接第三方 RESTful API（如排行榜、登录系统、内容分发）；
- 你正在开发一个需要频繁与后端通信的多人游戏，希望避免手写 HTTP 请求和 JSON 解析；
- 你的 API 规范经常变更，希望通过重新导入 .yaml 自动更新 UE 端代码；
- 你希望将 API 调用暴露给蓝图设计师，无需 C++ 知识即可完成网络通信。

## 蓝图用法

> **注意**: 由于该插件仍处于实验阶段，公开的蓝图节点会随着生成的内容动态变化。以下节点为插件核心基础设施，非生成节点。

插件本身不提供固定蓝图节点，而是在导入 OpenAPI 规范后，自动为每个端点生成对应的蓝图可调用函数。这些函数将出现在蓝图图表中，函数名与端点操作对应（如 `GET_UserList`、`POST_CreateEntity`）。

### 核心节点（插件内置）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create HTTP Request` | 手动创建 HTTP 请求对象（低级用法，通常由自动生成代码内部使用） | `UWebAPIHttpRequest` |
| `Set Request Body` | 设置请求体（JSON/ZSON） | `UWebAPIHttpRequest` |
| `Parse Response` | 将 HTTP 响应解析为自动生成的结构体 | `UWebAPIDeveloperSettings` |

### 使用示例（蓝图描述）

1. **直接调用生成的端点函数**  
   在事件图表中右键输入 `GET_` 或 `POST_`，即可看到根据 OpenAPI 规范生成的函数。直接拖出并连接对应输入参数，执行后返回结构体变量（如 `FUserList`）。

2. **自动错误处理**  
   生成的函数会包含 `On Success` 与 `On Failure` 执行引脚，分别连接成功/失败分支，无需手动检查 HTTP 状态码。

3. **配置基础 URL**  
   打开项目设置 → 插件 → WebAPI，输入 API 的 Base URL 和默认 Headers。生成的请求会自动继承这些设置。

## C++ 用法

### 头文件引入

```cpp
#include "WebAPI.h"
#include "WebAPIDeveloperSettings.h"
#include "GeneratedAPI/MyAPI.h"       // 假设生成的 API 文件
```

### 基本用法

使用生成的 C++ 类发起请求（假设 OpenAPI 规范定义了 `GET /users`）：

```cpp
UMyAPI* MyAPI = NewObject<UMyAPI>();
MyAPI->GetUsers(
    [](const TArray<FUser>& Users)
    {
        // 成功回调
        UE_LOG(LogTemp, Log, TEXT("Fetched %d users"), Users.Num());
    },
    [](const FWebAPIError& Error)
    {
        // 失败回调
        UE_LOG(LogTemp, Error, TEXT("Request failed: %s"), *Error.Message);
    }
);
```

> **注意**: 实际生成的类名和函数名由 OpenAPI 规范和模板决定。上述示例仅演示典型调用模式。

### 进阶用法

自定义序列化/反序列化（通过 LiquidJS 模板）：

1. 复制 `Templates/GeneratedAPI` 目录到项目 `Plugins` 文件夹；
2. 修改 `.liquid` 模板文件，调整代码生成风格；
3. 在编辑器设置中指定自定义模板路径。

## Demo 示例

由于该插件核心功能依赖于外部 OpenAPI 规范，无法提供独立编译的静态示例。以下为使用该插件的最小项目结构：

**ProjectName.Build.cs** (需依赖的模块)
```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "WebAPI", "WebAPIOpenAPI", "WebAPILiquidJS"
});
```

**MyActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyActor.generated.h"

UCLASS()
class AMyActor : public AActor
{
    GENERATED_BODY()
public:
    virtual void BeginPlay() override;
};
```

**MyActor.cpp**
```cpp
#include "MyActor.h"
#include "WebAPIDeveloperSettings.h"
#include "GeneratedAPI/MyAPI.h"         // 由插件根据您的 OpenAPI 规范生成
#include "Dom/JsonObject.h"

void AMyActor::BeginPlay()
{
    Super::BeginPlay();
    
    // 创建生成的 API 实例（需提前导入规范并生成代码）
    UMyAPI* MyAPI = NewObject<UMyAPI>();
    if (MyAPI)
    {
        MyAPI->GetHealthCheck(
            [](const FString& Status)
            {
                UE_LOG(LogTemp, Log, TEXT("Health: %s"), *Status);
            },
            [](const FWebAPIError& Error)
            {
                UE_LOG(LogTemp, Error, TEXT("Failed: %s"), *Error.Message);
            }
        );
    }
}
```

> **说明**: 实际使用时请先通过编辑器导入 OpenAPI 规范（Window → WebAPI → Import），然后点击 Generate 生成项目文件。

## 模块依赖

使用 WebAPI 插件时，您的模块需在 `Build.cs` 中添加以下依赖：

| 模块 | 用途 |
|---|---|
| `WebAPI` | 核心运行时：类型定义、HTTP 客户端、JSON 序列化 |
| `WebAPIOpenAPI` | OpenAPI 规范解析（导入用，若只需运行时调用可不加） |
| `WebAPILiquidJS` | 模板引擎支持（运行时仍需，用于动态生成代码） |
| `WebAPIBlueprintGraph` | 蓝图节点支持（仅在编辑器有用，打包可忽略） |
| `WebAPIEditor` | 编辑器工具（打包可忽略） |
| `HTTP` | 底层 HTTP 客户端（非标准依赖，需显式添加） |

## 维护状态

### 近期更新

根据截至 2025-10-21 的 git log（位于 WebAPI 插件目录）：

- 2025-07-31 — 平台进程创建句柄规范更新（非功能性修复）  
- 2025-06-11 — 替换 FORCEINLINE 用法（代码风格微调）  
- 2024-11-22 — 修正 uplugin 描述文件同时标记为 Experimental 和 Beta 的问题  
- 2024-11-20 — 修复 MustImplement 元数据名称变更  
- 2024-11-15 — 初始提交：插件创建

### 维护评价

- **创建时间**：2024-11-15，距今约 11 个月。  
- **最近功能更新**：无实质性功能更新，多为引擎兼容性修复和元数据调整。  
- **活跃度**：实验性标签且 `EnabledByDefault=false`，属于未正式发布的早期功能。  
- **稳定性**：代码仍在频繁变动中，API 可能不向后兼容。  
- **推荐使用**：适合试验性项目或需要快速原型验证的场景；不建议用于生产环境。  
- **已知限制**：OpenAPI 规范支持的范围有限（主要覆盖 3.0 基础特性）；自定义模板需一定 LiquidJS 知识。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Web/WebAPI)
- [官方文档]（暂无）  
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Web/WebAPI/Tests)（若存在）