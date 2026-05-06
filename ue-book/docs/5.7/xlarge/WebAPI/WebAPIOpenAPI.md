# WebAPI

> Automated generation of web based APIs

| 属性 | 值 |
|---|---|
| 中文名 | WebAPI 生成 |
| 分类 | Web |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（代码模板） |
| 模块 | `WebAPI` (Runtime), `WebAPIBlueprintGraph` (Runtime), `WebAPIEditor` (Runtime), `WebAPILiquidJS` (Runtime), `WebAPIOpenAPI` (Runtime), `PLUGIN_NAMEGenerated` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-11-15 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Web/WebAPI) | |

## 用途

WebAPI 插件旨在根据 OpenAPI（Swagger V2 和 OpenAPI V3）规范文件自动生成 UE 端的网络 API 层代码。其核心转换逻辑由 **WebAPIOpenAPI** 模块实现，该模块负责：

- 解析 OpenAPI V2（Swagger）和 V3 格式的 JSON 或 YAML 描述文件。
- 将 API 端点、请求/响应模型、参数、枚举等转换为 UE 的 `UWebAPIDefinition` 资产。
- 结合 LiquidJS 模板引擎，从转换后的定义资产生成 C++ 或蓝图可用的 API 客户端代码。

此插件解决了传统手动编写网络绑定代码的痛点，特别适合拥有现成 OpenAPI 规格的后端服务，可大幅缩短集成时间。

## 使用场景

- **REST API 客户端自动生成**：你有一个后端 REST API，其结构已通过 OpenAPI 文档定义。通过 WebAPI 插件导入该文档，即可自动产生完整的 UE 客户端代码，包含类型定义、请求构建、响应解析等。
- **多版本 API 支持**：同时维护 Swagger V2 和 OpenAPI V3 的混合环境，插件内置两种规范的处理逻辑。
- **自定义代码生成**：利用 LiquidJS 模板和挂载点（hook），深度定制生成的代码风格和目录结构。

## 蓝图用法

**WebAPIOpenAPI 模块**不直接提供蓝图可调用节点。其功能主要面向编辑器资产导入流程（由工厂类 `UWebAPISwaggerFactory` 和 `UWebAPIOpenAPIFactory` 自动处理）以及 C++ 扩展。

用户可通过编辑器菜单 **文件 → 导入** 选择 `.json` / `.yaml` 文件，将其导入为 `UWebAPIDefinition` 资产。随后可使用 WebAPI 编辑器（位于 `WebAPIEditor` 模块）对定义进行预览、修改和生成代码。

## C++ 用法

通过 C++ 可直接在代码中调用 OpenAPI 转换引擎，适用于自动化导入流程或测试。

### 头文件引入

```cpp
#include "V2/WebAPISwaggerProvider.h"
#include "V3/WebAPIOpenAPIProvider.h"
#include "WebAPIDefinition.h"
```

### 基本用法

使用 `FWebAPISwaggerProvider` 或 `FWebAPIOpenAPIProvider` 将 OpenAPI 文件内容转换为 `UWebAPIDefinition` 资产。

```cpp
// Source: Engine/Plugins/Experimental/Web/WebAPI/Source/WebAPIOpenAPI/Private/V2/WebAPISwaggerProvider.cpp (近似用法)

UWebAPIDefinition* Definition = NewObject<UWebAPIDefinition>();
Definition->Init();

// 假设已从文件读取内容到 FileContents
const FString FileContents = ReadFileToString(TEXT("api.yaml"));

TSharedPtr<FWebAPISwaggerProvider> Provider = MakeShared<FWebAPISwaggerProvider>();
TFuture<EWebAPIConversionResult> ResultFuture = Provider->ConvertToWebAPISchema(Definition);
ResultFuture.Wait(); // 同步等待，实际建议用异步回调

EWebAPIConversionResult Result = ResultFuture.Get();
if (Result == EWebAPIConversionResult::Succeeded)
{
    // Definition 已填充解析后的 Schema，可进一步使用或生成代码
}
```

### 进阶用法

可直接使用 OpenAPI 内部 Schema 类解析原始 JSON，跳过 Provider 流程：

```cpp
// 参考 WebAPIOpenAPI 测试用例（虚）
#include "V2/WebAPISwaggerSchema.h"

TSharedRef<FJsonObject> JsonObject = ...; // 从文件解析
UE::WebAPI::OpenAPI::V2::FSwagger Swagger;
Swagger.FromJson(JsonObject);

// 访问解析后的信息
FString Host = Swagger.Host.Get(TEXT("localhost"));
TArray<TSharedPtr<UE::WebAPI::OpenAPI::V2::FPath>> Paths = Swagger.Paths;
```

对于 OpenAPI V3 使用 `UE::WebAPI::OpenAPI::V3::FOpenAPIObject` 同理。

## Demo 示例

以下示例演示如何从 C++ 导入 OpenAPI V3 文件并触发代码生成。

```cpp
// WebAPISample.h
#pragma once

#include "CoreMinimal.h"
#include "WebAPIDefinition.h"
#include "V3/WebAPIOpenAPIProvider.h"
#include "V3/WebAPIOpenAPIFactory.h"

class FWebAPIImportSample
{
public:
    static bool ImportOpenAPI(const FString& FilePath);
};

// WebAPISample.cpp
#include "WebAPISample.h"
#include "Misc/FileHelper.h"
#include "WebAPIDefinition.h"
#include "V3/WebAPIOpenAPIProvider.h"

bool FWebAPIImportSample::ImportOpenAPI(const FString& FilePath)
{
    // 1. 读取文件内容
    FString FileContents;
    if (!FFileHelper::LoadFileToString(FileContents, *FilePath))
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to load file: %s"), *FilePath);
        return false;
    }

    // 2. 创建定义资产
    UWebAPIDefinition* Definition = NewObject<UWebAPIDefinition>(GetTransientPackage());
    Definition->AddToRoot(); // 防止 GC
    Definition->Init();

    // 3. 使用 OpenAPI V3 Provider 转换
    TSharedPtr<FWebAPIOpenAPIProvider> Provider = MakeShared<FWebAPIOpenAPIProvider>();
    TFuture<EWebAPIConversionResult> Future = Provider->ConvertToWebAPISchema(Definition);
    Future.Wait();

    const EWebAPIConversionResult Result = Future.Get();
    if (Result != EWebAPIConversionResult::Succeeded)
    {
        UE_LOG(LogTemp, Warning, TEXT("OpenAPI conversion failed."));
        Definition->RemoveFromRoot();
        return false;
    }

    // 4. 保存定义资产到包（可选）
    // 使用 UPackage 序列化保存…

    UE_LOG(LogTemp, Log, TEXT("OpenAPI imported successfully."));

    // 5. 触发代码生成（通过 WebAPIEditor 模块）
    // 例如调用 UWebAPIDefinition::GenerateCode() 或编辑器命令

    Definition->RemoveFromRoot();
    return true;
}
```

**注意**：实际项目中建议将 `Definition` 持久化到资产包中，而非使用瞬态对象。

## 模块依赖

WebAPIOpenAPI 模块的构建依赖（基于头文件包含推断）：

| 模块 | 用途 |
|---|---|
| `WebAPI` | 核心定义类型（UWebAPIDefinition、UWebAPISchema 等）及 provider 接口 |
| `Json` | 解析 JSON 文件 |
| `JsonUtilities` | JSON 对象辅助操作 |

## 维护状态

### 近期更新

- 2025-07-31 `399ed9f8` — 修复 FWindowsPlatformProcess::CreateProc 等平台 API 手柄处理（非本模块直接改动）
- 2025-06-11 `afdf8d75` — 替换 Online 模块中的 FORCEINLINE 用法
- 2024-11-22 `36771d79` — 更新 uplugin 描述符，移除同时标记 Experimental 和 Beta 的重复字段
- 2024-11-20 `e2fe1c9e` — 修复属性 MustImplement 改为 ObjectMustImplement 元数据
- 2024-11-15 `a2c3875d` — 清理 FSlateFontInfo 构造函数

以上 log 为引擎全局提交，未直接反映 WebAPIOpenAPI 模块的专有改动。模块自创建以来（2024-11-15）未见功能性更新。

### 维护评价

- **创建时间**：2024-11-15（约 1 年前）
- **近期更新**：无针对该模块的实质性功能或修复提交
- **维护状态**：**实验性** – 插件标记为 `IsExperimentalVersion = true`，社区和官方使用记录较少。
- **已知问题**：暂未报告严重问题，但可能存在与 UE 编辑器版本兼容性风险。
- **推荐度**：⚠️ 适合新项目探索性使用；对于生产环境需谨慎，建议跟随引擎预览版更新，并做好备份。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Web/WebAPI)
- 官方文档：无
- 测试用例：位于 `Engine/Plugins/Experimental/Web/WebAPI/Tests/`（部分模块测试）