# WebAPI

> Automated generation of web based APIs

| 属性 | 值 |
|---|---|
| 中文名 | 网页API生成器 |
| 分类 | Web |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图节点、编辑器资产类型、代码生成模板） |
| 模块 | `WebAPI` (Runtime), `WebAPIBlueprintGraph` (Runtime), `WebAPIEditor` (Runtime), `WebAPILiquidJS` (Runtime), `WebAPIOpenAPI` (Runtime), `PLUGIN_NAMEGenerated` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-11-15 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Web/WebAPI) | |

## 用途

WebAPI 插件是一个从 OpenAPI 规范（或其他来源）自动生成 UE C++ 代码的工具链。它允许开发者定义 Web API 的 schema（服务、操作、模型、枚举等），然后一键生成对应的 `UObject` 派生类、函数库和 HTTP 请求封装。核心工作流是：导入 API 描述文件 → 在编辑器中检查、编辑 schema → 生成 C++ 代码到目标模块。

此插件解决以下问题：
- 手动编写 REST API 客户端代码繁琐且容易出错
- API 变更后需要同步更新全部绑定代码
- 维护 API 类型（模型、枚举）与 UE 类型的映射

## 使用场景

- **对接 RESTful 服务**：例如你想让游戏客户端与一个提供 JSON 数据的外部后端通信，导入其 OpenAPI 描述，即可生成类型安全的 C++ 调用代码。
- **自动生成 UObject 模型**：将 API 返回的复杂 JSON 结构自动转化为 `UWebAPIModel` 子类，支持嵌套和枚举。
- **编辑器集成工作流**：通过 WebAPI 资产编辑器可视化查看服务、操作、模型树，并控制代码生成的开关。

## 蓝图用法

WebAPI 插件主要面向 C++ 开发者，但一些基础操作通过 `WebAPIBlueprintGraph` 模块暴露少量蓝图节点。由于当前模块 `WebAPIEditor` 是编辑器工具，不直接提供运行时蓝图节点。如需在蓝图中发起 HTTP 请求，请使用引擎内置的 `Http` 模块，或通过生成的 C++ 函数暴露给蓝图。

**注意**：注册到蓝图的节点（如 `Call WebAPI Operation`）由 `WebAPIBlueprintGraph` 模块提供，不在本文档范围。

## C++ 用法

以下示例基于 `WebAPIEditor` 模块中的测试代码 `Private/Tests/WebAPIJsonTestData.h` 和公开头文件。

### 头文件引入

```cpp
#include "WebAPIEditorModule.h"               // 模块入口
#include "Details/ViewModels/WebAPIViewModel.h" // 视图模型基类
#include "CodeGen/Dom/WebAPICodeGenBase.h"      // 代码生成基础类
```

### 基本用法

**1. 获取插件模块实例并注册自定义 Provider**

```cpp
#include "IWebAPIEditorModule.h"

void RegisterMyProvider()
{
    if (IWebAPIEditorModule* Module = FModuleManager::GetModulePtr<IWebAPIEditorModule>("WebAPIEditor"))
    {
        TSharedRef<IWebAPIProviderInterface> MyProvider = MakeShared<FMyProvider>();
        Module->AddProvider(TEXT("MyProvider"), MyProvider);
    }
}
```

**2. 使用 JSON 解析工具读取 API 响应**

位于 `Private/Tests/` 中的 `FTestStruct` 演示了如何通过 `Json::TryGetField` 从 `FJsonObject` 反序列化数据：

```cpp
// 来源：Engine/Plugins/Experimental/Web/WebAPI/Source/WebAPIEditor/Private/Tests/WebAPIJsonTestData.h
#include "WebAPIJsonUtilities.h"

bool FromJson(const TSharedPtr<FJsonObject>& InJsonObject)
{
    bool bResult = false;
    bResult |= Json::TryGetField(InJsonObject, TEXT("TestFloat"), TestFloat);
    bResult |= Json::TryGetField(InJsonObject, TEXT("TestText"), TestText);
    bResult |= Json::TryGetField(InJsonObject, TEXT("TestPtrOfContainingType"), TestPtrOfContainingType);
    bResult |= Json::TryGetField(InJsonObject, TEXT("ArrayOfOuterType"), ArrayOfOuterType);
    return bResult;
}
```

**3. 代码生成 DOM 对象构建**

```cpp
#include "CodeGen/Dom/WebAPICodeGenEnum.h"

FWebAPICodeGenEnum Enum;
Enum.Name = FWebAPITypeNameVariant(TEXT("EMyStatus"));
Enum.Values.Emplace(FWebAPICodeGenEnumValue{ TEXT("Active"), TEXT("Active"), TEXT("active"), TEXT("Active status"), 0 });
Enum.Module = TEXT("MyAPIModule");
// 然后将其添加到 FWebAPICodeGenFile 并写入磁盘
```

### 进阶用法

**结合视图模型在编辑器 UI 中显示 API Schema**

`IWebAPIViewModel` 是编辑器树形视图的基础。以下代码创建一个根定义视图模型并获取其下的 schema、服务、操作：

```cpp
// 假设已有 UWebAPIDefinition* Definition
TSharedRef<FWebAPIDefinitionViewModel> DefVM = FWebAPIDefinitionViewModel::Create(Definition);
TSharedPtr<FWebAPISchemaViewModel> SchemaVM = DefVM->GetSchema(); // 内部持有
TArray<TSharedPtr<IWebAPIViewModel>> Children;
SchemaVM->GetChildren(Children); // 填充 Service / Model / Enum 等
```

**监听编辑器选择事件**

`FWebAPIDefinitionDetailsCustomization::OnSchemaObjectSelected` 静态委托可用于在代码视图（`SWebAPICodeView`）中同步显示选中对象的生成代码：

```cpp
FWebAPIDefinitionDetailsCustomization::OnSchemaObjectSelected().AddLambda(
    [](const TWeakObjectPtr<UWebAPIDefinition>&, const TSharedPtr<IWebAPIViewModel>& SelectedVM)
    {
        if (SelectedVM && SelectedVM->HasCodeText())
        {
            FText Code = SelectedVM->GetCodeText();
            // 填充到编辑器中的代码查看 tab
        }
    }
);
```

## Demo 示例

一个完整的示例：创建 WebAPI 定义资产并触发代码生成。

### WebAPIDemo.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "WebAPIDefinition.h"
#include "WebAPIEditorModule.h"

class FWebAPIDemo
{
public:
    void RunDemo();
};
```

### WebAPIDemo.cpp

```cpp
#include "WebAPIDemo.h"
#include "EditorAssetLibrary.h"
#include "FileHelpers.h"

void FWebAPIDemo::RunDemo()
{
    // 1. 创建 WebAPIDefinition 资产
    UWebAPIDefinition* Definition = Cast<UWebAPIDefinition>(
        UEditorAssetLibrary::CreateAsset(
            UWebAPIDefinition::StaticClass(),
            TEXT("/Game/API/MyService"),
            TEXT("MyServiceDef"),
            EFileMediaType::Asset
        )
    );
    if (!Definition) return;

    // 2. 设置目标模块
    Definition->SetTargetModule(TEXT("MyGame"));

    // 3. 导入 OpenAPI 描述（假设已有 JSON 字符串）
    TSharedPtr<FJsonObject> JsonObject = MakeShared<FJsonObject>();
    // ... 填充 JSON 数据 ...
    Definition->ImportFromJson(JsonObject);

    // 4. 保存资产
    UPackage* Package = Definition->GetPackage();
    if (Package) UEditorAssetLibrary::SaveLoadedAsset(Definition, false);

    // 5. 通过工具栏命令执行生成
    if (IWebAPIEditorModule* Module = FModuleManager::GetModulePtr<IWebAPIEditorModule>("WebAPIEditor"))
    {
        // 假设我们有一个 asset editor toolkit 引用
        // Module->GetAssetEditorToolkit()->Generate();
    }
}
```

**注意**：以上代码为概念性示例，实际 API 可能因版本不同而有差异，请参考插件源码中的 `FWebAPIDefinitionAssetEditorToolkit::Generate()`。

## 模块依赖

`WebAPIEditor` 模块的 `Build.cs` 中包含以下独特依赖（省略常见 Core/Engine/UnrealEd 等）：

| 模块 | 用途 |
|---|---|
| `WebAPI` | 运行时核心数据模型（`UWebAPIDefinition`, `UWebAPIModel`, `UWebAPIService` 等） |
| `WebAPIOpenAPI` | OpenAPI 规范导入器 |
| `WebAPILiquidJS` | LiquidJS 模板引擎，用于代码生成模板渲染 |
| `HTTP` | 在测试和 Provider 中发起 HTTP 请求 |
| `Json` | JSON 序列化/反序列化 |
| `EditorWidgets` | 编辑器 UI 组件（`SWebAPITreeView`） |
| `PropertyEditor` | 细节面板定制（`FWebAPIDefinitionDetailsCustomization`） |
| `PluginBrowser` | 插件向导扩展（`FWebAPIPluginWizardDefinition`） |

**全栈依赖**：`WebAPIEditor` 是编辑器模块，若要使用生成的运行时代码，目标模块只需依赖 `WebAPI`（Runtime）即可；若需蓝图集成，还需依赖 `WebAPIBlueprintGraph`；若需导入 OpenAPI，需在导入工具中配置 `WebAPIOpenAPI`。

## 维护状态

### 近期更新

- 2025-07-31 `399ed9f8` — Make FWindowsPlatformProcess::CreateProc and FMacPlatformProcess::CreateProc specify the handles to （全局引擎更新，非 WebAPI 特定）
- 2025-06-11 `afdf8d75` — Replace some usages of FORCEINLINE with inline in Online modules.（全局引擎更新）
- 2024-11-22 `36771d79` — Updated uplugin descriptor files marked as both Experimental and Beta. Plugins with both flags in the descriptor will now assert.（修复插件描述文件实验性+测试版冲突）
- 2024-11-20 `e2fe1c9e` — Fixed object properties using MustImplement to now use ObjectMustImplement metadata（修复元数据属性）
- 2024-11-15 `a2c3875d` — Cleanup of FSlateFontInfo constructor across the solution（全局字体清理）

### 维护评价

- **创建时间**：2024-11-15，不到 1 年
- **最近更新频率**：最近三次 commit（2025-07 和 2025-06）均为引擎级别的非功能性改动，自 2024-11 创建以来没有实质性的新功能添加或 API 变更。
- **活跃度**：目前处于实验性阶段，基础框架搭建完毕，但后续更新频率较低。没有已知的重大 bug 报告，也没有废弃标记。
- **推荐使用**：对于需要自动生成 Web API 客户端的项目而言非常有用，但需注意插件仍标记为实验性，API 可能在未来版本中发生变化。建议在小型项目或原型中尝试，并做好随时调整的准备。

## 相关链接

- [源码（插件根目录）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Web/WebAPI)
- [WebAPIEditor 模块头文件](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Experimental/Web/WebAPI/Source/WebAPIEditor/Public)
- [测试代码示例](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Experimental/Web/WebAPI/Source/WebAPIEditor/Private/Tests/WebAPIJsonTestData.h)