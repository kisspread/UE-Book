# WebAPI

> Automated generation of web based APIs（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | Web API 自动生成 |
| 分类 | Web |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（API 模板资产、代码生成模板） |
| 模块 | `WebAPI` (Runtime), `WebAPIBlueprintGraph` (Runtime), `WebAPIEditor` (Runtime), `WebAPILiquidJS` (Runtime), `WebAPIOpenAPI` (Runtime), `PLUGIN_NAMEGenerated` (Runtime) |
| 实验性 | ⚦️ 是 |
| 创建时间 | 2022-07-11 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Web/WebAPI) | |

## 用途

WebAPI 插件是一个**基于模板引擎（LiquidJS）的 Web API 代码生成系统**，其核心目的是将 UE 中的 `UWebAPIDefinition` 数据资产自动转化为可运行的 Web API 代码。

这个插件解决的关键问题：
1. **自动化生成**：开发者在 UE 编辑器中定义 API 接口结构，插件通过 LiquidJS 模板引擎自动生成对应的 C++ 源码和蓝图代码
2. **实时预览服务**：内嵌 Node.js 进程（WebApp），可在开发阶段实时提供 HTTP 和 WebSocket 服务，方便前端联调
3. **OpenAPI 兼容**：支持 OpenAPI 规范格式的 API 定义导入/导出
4. **蓝图集成**：提供蓝图图编辑器扩展，可在蓝图中直接使用生成的 API 节点

本质上，这是一个**"定义即服务"**的开发工具链，让 UE 项目能够快速暴露 Web API 给外部系统（如游戏管理后台、数据监控面板、第三方服务等）。

## 使用场景

- 你正在开发一个需要向 Web 前端暴露数据接口的 UE 服务端应用 → 用 WebAPI 定义接口并自动生成代码
- 你需要一个本地 HTTP/WebSocket 服务来调试 UE 内部逻辑 → 用 WebAPILiquidJS 内置的 Node.js Web 服务
- 你已有 OpenAPI/Swagger 定义文件，想在 UE 中生成对应的 C++ 代码 → 用 WebAPIOpenAPI 模块
- 你希望在蓝图中快速定义 Web 路由和处理逻辑 → 用 WebAPIBlueprintGraph 模块

## 蓝图用法

> 注：由于当前分析聚焦于 WebAPILiquidJS 子模块，完整的蓝图节点信息需参考 WebAPI 核心模块和 WebAPIBlueprintGraph 模块。以下为 WebAPILiquidJS 模块暴露的蓝图可用功能。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `IsAvailable` | 检查 LiquidJS 代码生成器是否可用（Node.js 环境就绪） | `UWebAPILiquidJSCodeGenerator` |
| `GenerateFile` | 根据 API 定义和文件配置生成代码文件 | `UWebAPILiquidJSCodeGenerator` |

### 使用示例（蓝图描述）

1. 在项目设置中配置 WebAPILiquidJS 的端口（默认 HTTP 33010、WebSocket 33020）
2. 创建一个 `UWebAPIDefinition` 数据资产，定义 API 接口结构
3. 通过编辑器工具或蓝图调用 `GenerateFile`，将定义生成为实际代码文件
4. 如需实时预览，WebApp 会自动在启动时运行（可在设置中关闭自动启动）

## C++ 用法

### 头文件引入

```cpp
#include "IWebAPILiquidJSModule.h"
#include "WebAPILiquidJSSettings.h"
#include "WebAPILiquidJSCodeGenerator.h"
#include "WebAPILiquidJSProcess.h"
```

### 基本用法：获取 LiquidJS 代码生成器

```cpp
// 获取 WebAPILiquidJS 模块实例
IWebAPILiquidJSModuleInterface& LiquidJSModule = FModuleManager::GetModuleChecked<IWebAPILiquidJSModuleInterface>("WebAPILiquidJS");

// 创建代码生成器实例
UWebAPILiquidJSCodeGenerator* CodeGen = NewObject<UWebAPILiquidJSCodeGenerator>();

// 检查生成器是否可用（Node.js 环境检查）
CodeGen->IsAvailable().Then([](TFuture<bool> Future)
{
    if (Future.Get())
    {
        UE_LOG(LogTemp, Log, TEXT("LiquidJS code generator is available"));
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("LiquidJS code generator is NOT available - check Node.js installation"));
    }
});
```

### 基本用法：生成代码文件

```cpp
// 假设已有 UWebAPIDefinition* Definition 和 FWebAPICodeGenFile 的定义
UWebAPILiquidJSCodeGenerator* CodeGen = NewObject<UWebAPILiquidJSCodeGenerator>();

TSharedPtr<FWebAPICodeGenFile> CodeGenFile = MakeShared<FWebAPICodeGenFile>();
// ... 配置 CodeGenFile 的属性 ...

CodeGen->GenerateFile(Definition, CodeGenFile).Then([](TFuture<EWebAPIGenerationResult> Future)
{
    EWebAPIGenerationResult Result = Future.Get();
    if (Result == EWebAPIGenerationResult::Succeeded)
    {
        UE_LOG(LogTemp, Log, TEXT("API code generated successfully"));
    }
});
```

### 进阶用法：手动控制 WebApp 进程

```cpp
// 模块内部通过 FWebAPILiquidJSProcess 管理 Node.js 进程
// 开发者可通过项目设置控制其行为

// 在 DefaultEngine.ini 中配置：
// [/Script/WebAPILiquidJS.WebAPILiquidJSSettings]
// bAutoStartWebServer=true
// bAutoStartWebSocketServer=true
// HttpServerPort=33010
// WebSocketServerPort=33020
// bForceWebAppBuildAtStartup=false
// bWebAppLogRequestDuration=true

// 获取服务 URL
const UWebAPILiquidJSSettings* Settings = GetDefault<UWebAPILiquidJSSettings>();
FString ServiceUrl = Settings->GetServiceUrl("/api/v1/users");
// 返回类似 "127.0.0.1:33010/api/v1/users"
```

## Demo 示例

### WebAPILiquidJS 自定义设置监听器

```cpp
// MyWebAPIListener.h
#pragma once

#include "CoreMinimal.h"
#include "WebAPILiquidJSSettings.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "MyWebAPIListener.generated.h"

UCLASS()
class UMyWebAPIListener : public UGameInstanceSubsystem
{
    GENERATED_BODY()

public:
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;
    virtual void Deinitialize() override;

    UFUNCTION(BlueprintCallable, Category = "WebAPI")
    FString GetApiEndpoint(const FString& Path) const;

private:
    void OnSettingsChanged(UObject* Object, struct FPropertyChangedEvent& Event);
};
```

```cpp
// MyWebAPIListener.cpp
#include "MyWebAPIListener.h"
#include "WebAPILiquidJSSettings.h"

void UMyWebAPIListener::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);

    // 监听设置变更
    UWebAPILiquidJSSettings* Settings = GetMutableDefault<UWebAPILiquidJSSettings>();
    Settings->OnSettingChanged().AddUObject(this, &UMyWebAPIListener::OnSettingsChanged);

    UE_LOG(LogTemp, Log, TEXT("WebAPI Listener initialized. Service URL: %s"), 
           *Settings->GetServiceUrl());
}

void UMyWebAPIListener::Deinitialize()
{
    Super::Deinitialize();
}

FString UMyWebAPIListener::GetApiEndpoint(const FString& Path) const
{
    const UWebAPILiquidJSSettings* Settings = GetDefault<UWebAPILiquidJSSettings>();
    return Settings->GetServiceUrl(Path);
}

void UMyWebAPIListener::OnSettingsChanged(UObject* Object, FPropertyChangedEvent& Event)
{
    UE_LOG(LogTemp, Log, TEXT("WebAPI settings changed, recomputing service URL"));
}
```

## 模块依赖

从各模块的 Build.cs 分析，该插件具有较多内部模块互相依赖关系。对外部使用者而言：

| 模块 | 用途 |
|---|---|
| `WebAPI` | 核心运行时模块，提供 API 定义和路由基础设施 |
| `WebAPILiquidJS` | LiquidJS 模板引擎集成，负责代码生成和 Node.js WebApp 进程管理 |
| `WebAPIOpenAPI` | OpenAPI/Swagger 规范支持，用于 API 定义的导入导出 |
| `WebAPIBlueprintGraph` | 蓝图图编辑器扩展，在蓝图中使用 API 节点 |
| `WebAPIEditor` | 编辑器工具和 UI |
| `Http` | UE 内置 HTTP 模块，用于运行时 HTTP 通信 |
| `Json` | JSON 序列化/反序列化支持 |
| `JsonUtilities` | JSON 与 UE 结构体的自动转换 |

> 注：该插件包含 6 个模块，具体依赖关系需参考各模块的 Build.cs。核心模块 WebAPI 是所有功能的基础。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量截断为浮点的编译警告 |
| 2026-04-30 | `361e0c84` | Refactored FJsonObject to support both FString and UE::FSharedString | 重构 FJsonObject 以支持 FString 和 FSharedString 两种字符串类型 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移日志宏从 UE_LOG 到 UE_LOGF |
| 2026-03-02 | `9758fa58` | FORT-984709 - Remove string duplication in FJsonObject to free memory | 移除 FJsonObject 中的字符串重复以释放内存 |
| 2026-02-18 | `516817d0` | PR #13954: fix(deps): on-headers is vulnerable to http response header manipulation (and other vulne | 修复依赖包 on-headers 的 HTTP 响应头注入漏洞 |

### 维护评价

- **状态**：**活跃维护中**。最近一次更新距今不到 1 个月（2026-05-13），且持续有功能性修复和重构
- **年龄**：创建于 2022 年 7 月，约 4 年历史
- **实验性标记**：仍标记为 `IsExperimentalVersion=true` 且 `EnabledByDefault=false`，表明 Epic 尚未将其视为生产就绪
- **注意事项**：
  - 该插件默认禁用，需在项目设置中手动启用
  - 依赖外部 Node.js 运行环境（LiquidJS WebApp）
  - 包含 206 个源文件，属于中大型插件，功能丰富但复杂度较高
  - 位于 `Experimental` 目录下，API 可能在未来版本中发生变化
- **推荐度**：如果你的项目确实需要从 UE 暴露 Web API，这是一个功能完善的方案，但需接受其"实验性"状态带来的潜在 API 变更风险。适合原型开发和内部工具场景。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Web/WebAPI)
- 官方文档（无）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Web/WebAPI/Tests)（如有）