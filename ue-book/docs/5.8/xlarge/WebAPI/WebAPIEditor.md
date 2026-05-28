# WebAPI

> Automated generation of web based APIs（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | Web API 代码生成器 |
| 分类 | Web |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（插件模板、蓝图资产） |
| 模块 | `WebAPI` (Runtime), `WebAPIBlueprintGraph` (Runtime), `WebAPIEditor` (Runtime), `WebAPILiquidJS` (Runtime), `WebAPIOpenAPI` (Runtime), `PLUGIN_NAMEGenerated` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-07-11 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/WebAPI) | |

## 用途

WebAPI 是一个**自动化 Web API 代码生成框架**，用于从外部 Web API 规范（如 OpenAPI/Swagger）解析并自动生成对应的 UE5 C++ 代码。它的核心目标是消除手动编写 HTTP 客户端代码的重复劳动。

**它解决的问题**：当你的游戏需要与外部 REST API 通信时（例如排行榜服务、支付网关、玩家数据后端），通常需要手动编写大量重复的请求/响应结构体、序列化/反序列化逻辑、HTTP 调用代码。WebAPI 通过以下流程自动完成这些工作：

1. **解析阶段**：通过 Provider（如 `WebAPIOpenAPI`）读取 API 规范文件（如 `.json` / `.yaml`），解析为中间 Schema 表示（`UWebAPISchema`）
2. **Schema 构建**：将 API 的 Services、Operations（端点）、Models（数据模型）、Enums 等构建为 UObject 树
3. **代码生成阶段**：通过 CodeGenerator 将 Schema 转换为 CodeGen 中间对象（`FWebAPICodeGenStruct`、`FWebAPICodeGenEnum` 等），再通过模板引擎（如 `WebAPILiquidJS` 使用 Liquid 模板）输出最终的 `.h` / `.cpp` 文件

这是一个**面向开发者的工具型插件**，不参与运行时逻辑（尽管模块类型标记为 Runtime）。

## 使用场景

- 你有一个第三方 REST API（如 Firebase、PlayFab、自定义后端），需要在 UE5 项目中调用 → 用 WebAPI 自动生成类型安全的客户端代码
- 你维护了一个 OpenAPI 规范文件，希望 UE5 代码与 API 规范保持同步 → 导入 .uplugin Definition 资产，一键重新生成
- 你需要自定义代码生成模板（如用 Liquid 模板语法控制输出格式） → 利用 `WebAPILiquidJS` 模块的模板能力
- 你有自己的 API 描述格式，需要接入 WebAPI 框架 → 实现自定义 `IWebAPIProviderInterface`

## 蓝图用法

WebAPI 本质上是一个**编辑器工具**，其公共 API 主要面向 C++ 扩展（Provider/CodeGenerator 接口），而非直接在蓝图中使用。蓝图相关的功能主要在 `WebAPIBlueprintGraph` 模块中（用于蓝图节点图集成），但该模块的源码未在本次分析中提供。

运行时生成的代码可以被蓝图调用，但 WebAPI 本身不暴露蓝图节点。

## C++ 用法

### 核心架构概念

WebAPI 的代码组织为分层架构：

| 层级 | 职责 | 代表类 |
|---|---|---|
| **Schema Dom** | API 的中间表示（数据模型） | `UWebAPISchema`, `UWebAPIOperation`, `UWebAPIModel`, `UWebAPIEnum` |
| **Type Registry** | 类型信息管理与查找 | `UWebAPITypeRegistry`, `UWebAPIStaticTypeRegistry` |
| **CodeGen Dom** | 代码生成的中间表示 | `FWebAPICodeGenStruct`, `FWebAPICodeGenEnum`, `FWebAPICodeGenFile` |
| **Provider** | 解析外部 API 规范 | `IWebAPIProviderInterface`, `UWebAPIDefinitionFactory` |
| **CodeGenerator** | 从 Schema 生成代码 | `IWebAPICodeGeneratorInterface`, `UWebAPICodeGeneratorBase` |

### 头文件引入

```cpp
// Schema 核心
#include "WebAPISchema.h"
#include "WebAPIType.h"
#include "WebAPIService.h"
#include "WebAPIOperation.h"
#include "WebAPIModel.h"
#include "WebAPIEnum.h"

// CodeGen 核心
#include "WebAPICodeGenerator.h"
#include "WebAPICodeGenFile.h"
#include "WebAPICodeGenStruct.h"
#include "WebAPICodeGenEnum.h"
#include "WebAPICodeGenProperty.h"

// JSON 工具
#include "WebAPIJsonUtilities.h"

// Definition 资产
#include "WebAPIDefinition.h"

// Provider 扩展
#include "IWebAPIProviderInterface.h"
```

### Schema Dom 基本用法

`UWebAPISchema` 是整个 API 的顶层容器，包含 Services 和 Models。

```cpp
// 来源: Public/Dom/WebAPISchema.h
// 创建一个新的 Schema
UWebAPISchema* Schema = NewObject<UWebAPISchema>();
Schema->APIName = TEXT("MyGameAPI");
Schema->Version = TEXT("1.0");
Schema->Host = TEXT("api.example.com");
Schema->BaseUrl = TEXT("/v1");

// 获取或创建一个 Service（服务分组）
TObjectPtr<UWebAPIService> UserService = Schema->GetOrMakeService(TEXT("Users"));

// 添加一个 Model（数据模型）
// 先创建 TypeInfo
TObjectPtr<UWebAPITypeInfo> TypeInfo = Schema->TypeRegistry->GetOrMakeGeneratedType(
    EWebAPISchemaType::Model, 
    TEXT("UserProfile"), 
    TEXT("user_profile")
);

// 添加 Model 并设置属性
UWebAPIModel* ProfileModel = Schema->AddModel<UWebAPIModel>(TypeInfo);
UWebAPIProperty* NameProp = NewObject<UWebAPIProperty>(ProfileModel);
NameProp->Name = FWebAPINameInfo(TEXT("DisplayName"), TEXT("display_name"));
NameProp->Type = FWebAPITypeNameVariant(Schema->TypeRegistry->FindGeneratedType(
    EWebAPISchemaType::Model, TEXT("String")));
ProfileModel->Properties.Add(NameProp);

// 添加一个 Operation（API 端点）
UWebAPIOperation* GetUserOp = NewObject<UWebAPIOperation>(Schema);
GetUserOp->Name = FWebAPITypeNameVariant(TEXT("GetUser"));
GetUserOp->Verb = TEXT("GET");
GetUserOp->Path = TEXT("/users/{userId}");
GetUserOp->Service = UserService;
UserService->Operations.Add(GetUserOp);

// 遍历整个 Schema（递归访问所有元素）
Schema->Visit([](IWebAPISchemaObjectInterface*& InElement)
{
    // 处理每个 Schema 元素
});
```

### Operation 参数存储类型

```cpp
// 来源: Public/Dom/WebAPIOperation.h
// 参数可以存储在 HTTP 请求的不同位置
UWebAPIOperationParameter* Param = NewObject<UWebAPIOperationParameter>(Request);
Param->Storage = EWebAPIParameterStorage::Path;   // URL 路径: /users/{id}
Param->Storage = EWebAPIParameterStorage::Query;  // 查询参数: ?key=value
Param->Storage = EWebAPIParameterStorage::Header; // 请求头: key: value
Param->Storage = EWebAPIParameterStorage::Cookie; // Cookie: key=value
Param->Storage = EWebAPIParameterStorage::Body;   // 请求体: JSON
```

### TypeRegistry 类型注册

```cpp
// 来源: Public/Dom/WebAPITypeRegistry.h
// 静态类型注册表（引擎子系统，内置类型）
UWebAPIStaticTypeRegistry* StaticRegistry = GEditor->GetEditorSubsystem<UWebAPIEditorSubsystem>()->GetStaticTypeRegistry();

// 查找内置类型
const TObjectPtr<UWebAPITypeInfo>* FoundType = StaticRegistry->FindBuiltinType(TEXT("String"));

// 内置类型是预定义的
TObjectPtr<UWebAPITypeInfo> StringType = StaticRegistry->String;    // FString
TObjectPtr<UWebAPITypeInfo> Int32Type = StaticRegistry->Int32;      // int32
TObjectPtr<UWebAPITypeInfo> BoolType = StaticRegistry->Boolean;     // bool
TObjectPtr<UWebAPITypeInfo> JsonObjType = StaticRegistry->JsonObject; // TSharedPtr<FJsonObject>

// Schema 级别的类型注册表（每个 Definition 独立）
UWebAPITypeRegistry* SchemaTypeRegistry = Schema->TypeRegistry;
TObjectPtr<UWebAPITypeInfo> GeneratedType = SchemaTypeRegistry->GetOrMakeGeneratedType(
    EWebAPISchemaType::Model, TEXT("User"), TEXT("user"));
```

### JSON 工具用法

```cpp
// 来源: Public/WebAPIJsonUtilities.h
// WebAPI 提供了一套模板化的 JSON 反序列化工具

// 读取数值
double Value;
UE::Json::TryGetField(JsonObject, TEXT("score"), Value);

// 读取字符串
FString Name;
UE::Json::TryGetField(JsonObject, TEXT("name"), Name);

// 读取数组
TArray<int32> Scores;
UE::Json::TryGetField(JsonObject, TEXT("scores"), Scores);

// 读取 Map
TMap<FString, int32> Stats;
UE::Json::TryGetField(JsonObject, TEXT("stats"), Stats);

// 读取枚举
TMap<FString, EMyEnum> EnumMap = { {TEXT("Active"), EMyEnum::Active} };
EMyEnum EnumValue;
UE::Json::TryGetField(JsonObject, TEXT("status"), EnumValue, EnumMap);

// TJsonReference - 延迟解析的 JSON 引用
// 支持 $ref 语法（如 OpenAPI 中的 "#/components/schemas/User"）
TJsonReference<FWebAPIModel> ModelRef;
ModelRef.ResolveDeferred(TEXT("#/components/schemas/User"));
// 稍后解析
ModelRef.TryResolve(RootObject, [](TSharedRef<FJsonObject>& InObj) -> FWebAPIModel*
{
    // 从 JSON 对象构造 Model
    return nullptr;
});
```

### 实现自定义 CodeGenerator

```cpp
// 来源: Public/CodeGen/WebAPICodeGenerator.h
// 继承 UWebAPICodeGeneratorBase 实现自定义代码生成器

class UMyCodeGenerator : public UWebAPICodeGeneratorBase
{
    GENERATED_BODY()

public:
    // 检查生成器是否可用（例如检查模板文件是否存在）
    virtual TFuture<bool> IsAvailable() override
    {
        return Async(EAsyncExecution::Thread, []() -> bool
        {
            return true;
        });
    }

    // 处理单个 Model（结构体）
    virtual TFuture<EWebAPIGenerationResult> GenerateModel(
        const TWeakObjectPtr<UWebAPIDefinition>& InDefinition,
        const TSharedPtr<FWebAPICodeGenStruct>& InStruct) override
    {
        // InStruct 已从 UWebAPIModel 转换而来
        // 可以直接使用 InStruct->Name, InStruct->Properties 等
        return Async(EAsyncExecution::Thread, [this, InStruct]() -> EWebAPIGenerationResult
        {
            // 生成代码...
            return EWebAPIGenerationResult::Succeeded;
        });
    }

    // 处理单个 Enum
    virtual TFuture<EWebAPIGenerationResult> GenerateEnum(
        const TWeakObjectPtr<UWebAPIDefinition>& InDefinition,
        const TSharedPtr<FWebAPICodeGenEnum>& InEnum) override
    {
        // InEnum->Values 包含所有枚举值
        return Async(EAsyncExecution::Thread, [InEnum]() -> EWebAPIGenerationResult
        {
            return EWebAPIGenerationResult::Succeeded;
        });
    }
};
```

### 注册 Provider 和 CodeGenerator

```cpp
// 来源: Private/WebAPIEditorModule.h
// 在你的编辑器模块 StartupModule() 中注册

IWebAPIEditorModuleInterface& WebAPIModule = IWebAPIEditorModuleInterface::Get();

// 注册 Provider（API 规范解析器）
TSharedRef<IWebAPIProviderInterface> MyProvider = MakeShared<FMyAPIProvider>();
WebAPIModule.AddProvider(FName("MyAPIFormat"), MyProvider);

// 注册 CodeGenerator（代码生成器）
WebAPIModule.AddCodeGenerator(FName("MyCodeGen"), UMyCodeGenerator::StaticClass());

// 监听 Provider 变化
WebAPIModule.OnProvidersChanged().AddLambda([]()
{
    // 重新获取所有 Provider
    TArray<TSharedRef<IWebAPIProviderInterface>> Providers;
    WebAPIModule.GetProviders(Providers);
});
```

## Demo 示例

以下示例展示如何以编程方式构建一个最小的 WebAPI Schema 并导出为 JSON：

```cpp
// WebAPISchemaExample.h
#pragma once

#include "CoreMinimal.h"
#include "Dom/WebAPISchema.h"
#include "Dom/WebAPIService.h"
#include "Dom/WebAPIOperation.h"
#include "Dom/WebAPIModel.h"
#include "Dom/WebAPITypeRegistry.h"

class FWebAPISchemaExample
{
public:
    static void BuildExampleSchema(UWebAPISchema* InSchema);
};
```

```cpp
// WebAPISchemaExample.cpp
#include "WebAPISchemaExample.h"
#include "WebAPIJsonUtilities.h"

void FWebAPISchemaExample::BuildExampleSchema(UWebAPISchema* InSchema)
{
    if (!InSchema || !InSchema->TypeRegistry)
    {
        return;
    }

    // 配置 API 基本信息
    InSchema->APIName = TEXT("GameLeaderboard");
    InSchema->Version = TEXT("v1");
    InSchema->Host = TEXT("leaderboard.example.com");
    InSchema->BaseUrl = TEXT("/api/v1");

    // 注册一个自定义类型
    UWebAPITypeRegistry* TypeReg = InSchema->TypeRegistry;
    TObjectPtr<UWebAPITypeInfo> ScoreType = TypeReg->GetOrMakeGeneratedType(
        EWebAPISchemaType::Model,
        TEXT("ScoreEntry"),
        TEXT("score_entry")
    );

    // 创建 Model
    UWebAPIModel* ScoreModel = InSchema->AddModel<UWebAPIModel>(ScoreType);

    // 添加属性: playerName (string)
    UWebAPIProperty* NameProp = NewObject<UWebAPIProperty>(ScoreModel);
    NameProp->Name = FWebAPINameInfo(TEXT("PlayerName"), TEXT("player_name"));
    NameProp->Type = FWebAPITypeNameVariant(InSchema->TypeRegistry->GetOrMakeGeneratedType(
        EWebAPISchemaType::Model, TEXT("FString"), TEXT("string")));
    ScoreModel->Properties.Add(NameProp);

    // 添加属性: score (int32)
    UWebAPIProperty* ScoreProp = NewObject<UWebAPIProperty>(ScoreModel);
    ScoreProp->Name = FWebAPINameInfo(TEXT("Score"), TEXT("score"));
    ScoreProp->Type = FWebAPITypeNameVariant(InSchema->TypeRegistry->GetOrMakeGeneratedType(
        EWebAPISchemaType::Model, TEXT("int32"), TEXT("int32")));
    ScoreModel->Properties.Add(ScoreProp);

    // 创建 Service
    TSoftObjectPtr<UWebAPIService> LeaderboardService = InSchema->GetOrMakeService(TEXT("Leaderboard"));

    // 创建 Operation: GET /scores
    UWebAPIOperation* GetScoresOp = NewObject<UWebAPIOperation>(InSchema);
    GetScoresOp->Name = FWebAPITypeNameVariant(TEXT("GetTopScores"));
    GetScoresOp->Verb = TEXT("GET");
    GetScoresOp->Path = TEXT("/scores");
    GetScoresOp->Description = TEXT("Retrieve the top scores leaderboard");
    GetScoresOp->Service = LeaderboardService;

    // 创建请求
    GetScoresOp->Request = NewObject<UWebAPIOperationRequest>(GetScoresOp);

    // 添加 limit 查询参数
    UWebAPIOperationParameter* LimitParam = NewObject<UWebAPIOperationParameter>(GetScoresOp->Request);
    LimitParam->Name = FWebAPINameInfo(TEXT("Limit"), TEXT("limit"));
    LimitParam->Type = FWebAPITypeNameVariant(InSchema->TypeRegistry->GetOrMakeGeneratedType(
        EWebAPISchemaType::Model, TEXT("int32"), TEXT("int32")));
    LimitParam->Storage = EWebAPIParameterStorage::Query;
    LimitParam->bIsRequired = false;
    GetScoresOp->Request->Parameters.Add(LimitParam);

    // 创建响应: 200 OK
    UWebAPIOperationResponse* Response = NewObject<UWebAPIOperationResponse>(GetScoresOp);
    Response->Code = 200;
    Response->Message = TEXT("Success");
    GetScoresOp->Responses.Add(Response);

    LeaderboardService->Operations.Add(GetScoresOp);

    // 导出 Schema 为 JSON（用于调试）
    TSharedPtr<FJsonObject> Json;
    if (InSchema->ToJson(Json))
    {
        FString OutputString;
        TSharedRef<TJsonWriter<>> Writer = TJsonWriterFactory<>::Create(&OutputString);
        FJsonSerializer::Serialize(Json.ToSharedRef(), Writer);
        UE_LOG(LogTemp, Log, TEXT("Schema JSON:\n%s"), *OutputString);
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `LiquidJS` | Liquid 模板引擎，用于 CodeGen 模板渲染 |
| `HTTP` | HTTP 请求发送 |
| `Json` / `JsonUtilities` | JSON 解析与序列化 |
| `AssetRegistry` | 资产发现与注册 |
| `GraphEditor` | 蓝图节点图编辑器集成 |
| `MessageLog` | 编辑器消息日志系统 |
| `ToolMenus` | 编辑器工具栏/菜单扩展 |
| `DesktopPlatform` | 文件对话框（模块选择器） |
| `ClassViewer` | 类选择器 UI |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 到 float 的截断警告 |
| 2026-04-30 | `361e0c84` | Refactored FJsonObject to support both FString and UE::FSharedString | 重构 FJsonObject 以同时支持 FString 和 SharedString |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移 UE_LOG 宏到 UE_LOGF |
| 2026-03-02 | `9758fa58` | FORT-984709 - Remove string duplication in FJsonObject to free memory | 消除 FJsonObject 中的字符串重复以释放内存 |
| 2026-02-18 | `516817d0` | PR #13954: fix(deps): on-headers is vulnerable to http response header manipulation (and other vulne | 修复 on-headers 依赖漏洞 |

### 维护评价

**维护中（活跃）**。该插件创建于 2022 年 7 月（约 4 年前），最近一次更新在 2026 年 5 月，更新频率稳定（约每月一次）。近期更新主要是：

- **引擎级重构适配**：随 UE 引擎主干的 API 变更进行同步更新（如 FJsonObject 重构、UE_LOG 迁移）
- **性能优化**：内存使用优化
- **编译器警告修复**：保持代码质量

需要注意的是：
- **实验性插件**：`IsExperimentalVersion=true`，API 可能在后续版本中发生 breaking changes
- **默认未启用**：`EnabledByDefault=false`，需要在插件管理器中手动启用
- 近期更新多为引擎级适配而非功能增强，说明该插件可能处于功能稳定但尚未正式毕业的状态
- **推荐用于原型开发和内部工具**，生产环境使用需评估稳定性风险

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/WebAPI)
- [官方文档]()（无）