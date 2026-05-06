# Interchange OpenUSD

> Allows translation of OpenUSD files via the Interchange framework

| 属性 | 值 |
|---|---|
| 中文名 | 通用USD导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、设置） |
| 模块 | `InterchangeOpenUSDEditor` (Runtime), `InterchangeOpenUSDImport` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-10-02 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Interchange/Extensions/OpenUSD) | |

---

## 用途

通过 Unreal Engine 的 **Interchange** 框架导入 Pipe 管道中的 **OpenUSD** （Universal Scene Description）文件。该插件将 USD 文件作为 Interchange 源，利用 Interchange 的资产生成管线（Translators、Pipelines、Factory）实现 USD 数据的高效导入和重新导入，同时支持 **Nanite** 细化网格、细分曲面等现代渲染特性。

解决的核心问题：在已有 Interchange 生态内统一管理 USD 资产的导入，避免使用老旧的非 Interchange 路径，提供可配置的导入选项（如渲染上下文、材质意图）以及与 USD 原生导入工具的兼容性。

---

## 使用场景

- 你的项目使用 **Interchange** 作为主要资产导入管线，需要导入 **USD** 场景（如角色、道具、环境）。
- 你需要对导入过程进行精细控制，例如选择特定的渲染上下文（如 `unreal` 、 `preview` ）、材质意图（ `preview` 、 `allPurpose` 、 `render` ）。
- 希望利用 **Interchange** 的重导入功能和 **Nanite** 支持，实现迭代开发。
- 需要在编辑器中对 USD 导入设置进行图形化调整（通过 `UInterchangeUsdTranslatorSettings` 及其属性定制）。

---

## 蓝图用法

本插件主要提供对 USD 导入设置的配置，在蓝图中通常通过 **导入选项** 节点或 **Interchange Translator** 设置进行操作。由于插件核心逻辑在 C++ 层，蓝图可用的关键节点如下：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `获取 Interchange 翻译器设置（USD）` | 获取当前 Interchange 任务的 USD 翻译器设置对象，用于调整导入参数。 | `UInterchangeUsdTranslatorSettings` |
| `设置渲染上下文` | 指定 USD 导入时使用的渲染上下文（如 `unreal` 、 `preview` 等）。 | `UInterchangeUsdTranslatorSettings` |
| `设置材质意图` | 指定 USD 导入时使用的材质意图。 | `UInterchangeUsdTranslatorSettings` |
| `设置细分层级` | 控制 USD 细分曲面的应用等级（0=关闭，最高为 3）。 | `UInterchangeUsdTranslatorSettings` |

> 注意：上述蓝图节点仅在 **Interchange** 导入流程的上下文中可用，通常用于自定义 Interchange Pipeline 或 BeforeImport 事件。

### 使用示例（蓝图描述）

1. **创建自定义 Interchange Pipeline**：在蓝图资产中创建 `InterchangePipelineBase` 子类，覆盖 `OnPipelineStartup` 事件。
2. **在事件中获取 USD 翻译器设置**：使用 `获取 Interchange 翻译器设置（USD）` 节点，节点输入为当前的 `UInterchangeTranslatorBase` 或将导入数据传入。
3. **配置属性**：将返回的 `UInterchangeUsdTranslatorSettings` 对象连接到 `设置渲染上下文` 节点，并将 `RenderContext` 设置为 `unreal`。类似地设置 `MaterialPurpose` 和 `SubdivisionLevel`。
4. **完成**：Pipeline 将在导入时应用这些设置。

---

## C++ 用法

### 头文件引入

```cpp
#include "InterchangeOpenUSDEditorModule.h"       // 编辑器模块
#include "InterchangeUsdTranslatorSettingsCustomization.h" // 设置自定义（编辑器）
#include "InterchangeOpenUSDImport.h"              // 实际导入模块（如有）
```

### 基本用法

通过 **Interchange** 框架启动 USD 导入时，Interchange 会自动识别 `.usd` 、 `.usda` 、 `.usdc` 文件并创建对应的 `UInterchangeUsdTranslator`。开发者可以在自定义 `UInterchangePipelineBase` 中获取并修改翻译器设置：

```cpp
// 假设 MyPipeline 继承自 UInterchangePipelineBase
void UMyPipeline::ExecutePipeline(UInterchangeBaseNodeContainer* NodeContainer,
                                   const TArray<UInterchangeSourceData*>& SourceDatas)
{
    // 获取 USD 翻译器设置对象
    // 在 Interchange 世界中，翻译器设置通常通过源数据附加的资产对象访问
    UInterchangeUsdTranslatorSettings* UsdSettings = nullptr;
    if (UInterchangeTranslatorBase* Translator = Cast<UInterchangeTranslatorBase>(GetTranslator()))
    {
        UsdSettings = Cast<UInterchangeUsdTranslatorSettings>(Translator->GetSettings());
    }
    if (!UsdSettings) return;

    // 修改设置
    UsdSettings->RenderContext = TEXT("unreal");
    UsdSettings->MaterialPurpose = TEXT("preview");
    UsdSettings->SubdivisionLevel = 2;
}
```

> 来源：根据 Interchange 框架文档及插件源码推断（`InterchangeUsdTranslatorSettings` 为 `UObject` 子类，属性为 `FString` 和 `int32`）

### 进阶用法

当需要在编辑器中进行更复杂的设置自定义时，可使用 `FInterchangeUsdTranslatorSettingsCustomization` 类，它提供了下拉框选项（渲染上下文、材质意图）的详细定制：

```cpp
// 在模块 StartupModule 中注册自定义布局
void FInterchangeOpenUSDEditorModule::StartupModule()
{
    // 注册细节定制
    static FName PropertyEditorModule("PropertyEditor");
    auto& PropertyModule = FModuleManager::LoadModuleChecked<FPropertyEditorModule>(PropertyEditorModule);
    PropertyModule.RegisterCustomClassLayout(
        UInterchangeUsdTranslatorSettings::StaticClass()->GetFName(),
        FOnGetDetailCustomizationInstance::CreateStatic(&FInterchangeUsdTranslatorSettingsCustomization::MakeInstance)
    );
}
```

该自定义布局会将 `RenderContext` 和 `MaterialPurpose` 的属性编辑从普通文本框替换为下拉框，并预置常用选项（`unreal`、`preview`、`allPurpose`、`render` 等）。

---

## Demo 示例

以下为在 C++ 中创建一个简单的 **Interchange Pipeline**，配置 USD 翻译器设置的完整示例（.h + .cpp）。

### MyUsdPipeline.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "InterchangePipelineBase.h"
#include "MyUsdPipeline.generated.h"

UCLASS(BlueprintType)
class MYPROJECT_API UMyUsdPipeline : public UInterchangePipelineBase
{
    GENERATED_BODY()

public:
    virtual void ExecutePipeline(UInterchangeBaseNodeContainer* NodeContainer,
                                 const TArray<UInterchangeSourceData*>& SourceDatas) override;
};
```

### MyUsdPipeline.cpp

```cpp
#include "MyUsdPipeline.h"
#include "InterchangeOpenUSDImport.h"          // 包含 UInterchangeUsdTranslatorSettings
#include "InterchangeTranslatorBase.h"

void UMyUsdPipeline::ExecutePipeline(UInterchangeBaseNodeContainer* NodeContainer,
                                      const TArray<UInterchangeSourceData*>& SourceDatas)
{
    // 获取翻译器设置（需确保当前任务使用了 USD 翻译器）
    UInterchangeUsdTranslatorSettings* UsdSettings = nullptr;
    if (UInterchangeTranslatorBase* Translater = GetTranslator())
    {
        UsdSettings = Cast<UInterchangeUsdTranslatorSettings>(Translater->GetSettings());
    }

    if (!UsdSettings)
    {
        UE_LOG(LogTemp, Warning, TEXT("MyUsdPipeline: No USD translator settings found."));
        return;
    }

    // 设置导入参数
    UsdSettings->RenderContext = TEXT("unreal");
    UsdSettings->MaterialPurpose = TEXT("preview");
    UsdSettings->SubdivisionLevel = 2;
    UsdSettings->bImportMeshLODs = true;
    UsdSettings->bImportCollision = false;

    // 注意：其他参数如 bUseNewMeshes 等也可在此设置
}
```

将此 Pipeline 添加至 Interchange 项目设置或通过编程方式注册，即可在导入 USD 时自动应用自定义设置。

---

## 模块依赖

| 模块 | 用途 |
|---|---|
| `InterchangeCore` | Interchange 框架核心管线 |
| `InterchangeDispatcher` | 用于异步导入处理 |
| `USDImporter` | 原生 USD 解析与转换逻辑 |
| `USDClasses` | USD 相关基础类（如 `UUsdAssetCache` ） |
| `UnrealUSDWrapper` | USD 库封装及底层 API 调用 |

> 注意：`InterchangeOpenUSDEditor` 额外依赖 `PropertyEditor` 用于细节定制，但属于常见编辑器依赖，未列出。

---

## 维护状态

插件为实验性，处于活跃开发阶段。

### 近期更新

- 2025-12-18 `3f562d0` — 修复当 Interchange 栈名称被修改时引起的崩溃
- 2025-10-16 `09310c6` — USD Interchange Nanite 组合体重新导入修复
- 2025-10-03 `24fcc14` — 回退 CL46528816
- 2025-10-03 `a8f2831` — Interchange USD：为细分层级属性设置与旧版 USD 类似的 min/max 范围
- 2025-10-02 `56e5b33` — USD：修复重复的 LOCTEXT 键

### 维护评价

| 维度 | 评价 |
|---|---|
| 创建时间 | 2025-10-02，至今约 5 个月 |
| 最近更新 | 2025-12-18 仍有修复，周期约 2 个月 |
| 活跃度 | ⏳ 较活跃，但频率不高（每 2-3 个月一次） |
| 实验性 | 标记为实验性，可能 API 仍会变动 |
| 推荐度 | 🟡 可用于原型和早期项目，生产环境需评估稳定性 |

**警告**：由于插件仍处于实验阶段，且更新周期较长，建议在使用前备份现有导入配置，并密切关注引擎版本更新。

---

## 相关链接

- [源码目录](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Interchange/Extensions/OpenUSD)
- [Interchange 官方文档](https://docs.unrealengine.com/5.4/en-US/interchange-framework-in-unreal-engine/)
- [USD 导入测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Interchange/Extensions/OpenUSD/Tests)