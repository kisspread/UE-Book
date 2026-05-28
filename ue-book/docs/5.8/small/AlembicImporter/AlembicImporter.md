# Alembic Importer

> Support importing Alembic files（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 动画缓存导入器 |
| 分类 | Importers |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `AlembicImporter` (Editor), `AlembicLibrary` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2022-01-26 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/AlembicImporter) | |

## 用途

AlembicImporter 插件为 Unreal Engine 提供了导入 `.abc` 格式文件的能力。它不仅仅是简单的静态网格导入，更重要的是解决了从 DCC（数字内容创作）软件（如 Maya、Houdini、Blender 等）导出的**动画几何缓存**数据的导入问题。这意味着它可以将带有逐帧顶点动画、形变动画的角色、物体或特效动画无缝地带入引擎中，作为 `UGeometryCache` 资产使用，完美保留原始动画的每一帧细节。它是处理复杂动画资产流水线的核心工具。

## 使用场景

- **影视动画与预演**：将 Maya 或 Houdini 中制作的复杂角色表演、布料、流体或粒子特效动画，以几何缓存的形式导入 UE，用于虚拟制片或实时预览。
- **游戏过场动画**：导入由外部动画软件生成的高精度过场动画序列。
- **建筑可视化**：导入包含精确时间动画（如日光变化、人群流动）的模型。
- **资产流水线**：在需要版本迭代或从外部软件持续更新动画资产的团队中，作为标准的资产交换格式。

## 蓝图用法

此插件主要通过编辑器 UI 进行交互（导入对话框、重导入选项），其核心功能封装在工厂类和 Slate UI 中，**并未暴露为蓝图可调用函数**。主要的“蓝图”交互是：
1.  在内容浏览器中右键单击，选择 **“导入到...”**。
2.  选择一个 `.abc` 文件。
3.  在弹出的 **“Alembic 导入选项”** 窗口中进行配置。

### 核心节点

该插件的核心逻辑不体现在蓝图节点上，而是体现在编辑器导入流程中。

### 使用示例（蓝图描述）

由于不直接暴露蓝图节点，典型用法是通过编辑器操作：
1.  **内容浏览器** -> 右键 -> **导入资产**。
2.  选择 `.abc` 文件。
3.  在出现的 **“Alembic Import Options”** (SAlembicImportOptions) 对话框中：
    - 设置导入类型（静态网格、几何缓存、骨骼网格体）。
    - 选择要导入的轨道（如果有多个多边形网格轨道）。
    - 调整网格简化、时间范围等参数。
    - 点击 **“Import”** 按钮。

## C++ 用法

该插件的核心是 `UFactory` 子类和相关的导入器类，主要用于引擎内部的文件导入流程。开发者若需进行程序化导入或自定义导入逻辑，可以参考其结构。

### 头文件引入

```cpp
#include "AlembicImportFactory.h"
// 如果需要访问具体导入数据结构，可能需要
#include "AbcImportSettings.h"
```

### 基本用法

一个最基本的程序化导入 `.abc` 文件为 `UGeometryCache` 的流程（概念示例）：

```cpp
// 概念示例，非直接可用代码，需结合 Editor 模块和反馈上下文
#include "AlembicImportFactory.h"
#include "AbcImportSettings.h"

void ImportMyAbcFile(const FString& AbcFilePath, UObject* InParent)
{
    // 1. 创建或获取工厂实例
    UAlembicImportFactory* Factory = NewObject<UAlembicImportFactory>();
    
    // 2. 准备导入设置（通常来自 UI 或默认值）
    UAbcImportSettings* Settings = NewObject<UAbcImportSettings>();
    // 配置 Settings，例如：
    // Settings->ImportType = EAlembicImportType::GeometryCache;
    // Settings->bFlattenTracks = true;
    Factory->ImportSettings = Settings;
    Factory->bShowOption = false; // 不显示UI

    // 3. 执行导入
    bool bOperationCanceled = false;
    FFeedbackContext* Warn = GLog; // 使用日志作为反馈上下文
    UObject* ImportedAsset = Factory->FactoryCreateFile(
        UGeometryCache::StaticClass(), // 目标类，根据导入类型调整
        InParent,
        FName(TEXT("MyGeometryCache")),
        RF_Public | RF_Standalone,
        AbcFilePath,
        nullptr,
        Warn,
        bOperationCanceled
    );

    if (ImportedAsset)
    {
        UE_LOG(LogTemp, Log, TEXT("Successfully imported Alembic to: %s"), *ImportedAsset->GetPathName());
    }
}
```
*（注：此为基于 `FactoryCreateFile` 接口的概念演示，实际使用时需处理编辑器上下文和更复杂的错误处理。）*

### 进阶用法

更高级的用法是重导入（Reimport）。当你需要通过代码更新一个已存在的 `UGeometryCache` 或 `UStaticMesh` 资产时：

```cpp
// 假设你已经有一个指向已导入资产的指针 UGeometryCache* ExistingCache
void ReimportExistingAbcAsset(UObject* ExistingAsset)
{
    // 查找处理该资产类型的 ReimportHandler
    TArray<UFactory*> ReimportFactories;
    for (TObjectIterator<UClass> It; It; ++It)
    {
        if (It->IsChildOf(UFactory::StaticClass()) && !It->HasAnyClassFlags(CLASS_Abstract))
        {
            UFactory* Factory = Cast<UFactory>(It->GetDefaultObject());
            if (Factory && Factory->CanReimport(ExistingAsset, /*OutFilenames*/TArray<FString>()))
            {
                ReimportFactories.Add(Factory);
            }
        }
    }

    // 找到优先级最高的工厂（通常是 AlembicImportFactory）
    UFactory* BestFactory = nullptr;
    int32 HighestPriority = -1;
    for (UFactory* Factory : ReimportFactories)
    {
        int32 Priority = Factory->GetPriority();
        if (Priority > HighestPriority)
        {
            HighestPriority = Priority;
            BestFactory = Factory;
        }
    }

    if (BestFactory)
    {
        // 执行重导入
        FReimportHandler* ReimportHandler = static_cast<FReimportHandler*>(BestFactory);
        EReimportResult::Type Result = ReimportHandler->Reimport(ExistingAsset);
        
        switch (Result)
        {
        case EReimportResult::Succeeded:
            UE_LOG(LogTemp, Log, TEXT("Reimport succeeded."));
            break;
        case EReimportResult::Failed:
            UE_LOG(LogTemp, Error, TEXT("Reimport failed."));
            break;
        case EReimportResult::Cancelled:
            UE_LOG(LogTemp, Warning, TEXT("Reimport cancelled."));
            break;
        }
    }
}
```
*（注：重导入通常依赖于资产中存储的源文件路径 (`UAssetImportData`)。）*

## Demo 示例

这是一个最小化的、展示如何作为自定义工厂扩展导入流程的示例框架。

**MyAbcAnalyzerFactory.h**
```cpp
#pragma once
#include "Factories/Factory.h"
#include "MyAbcAnalyzerFactory.generated.h"

// 一个假想的、只分析 Alembic 文件结构的工厂
UCLASS()
class UMyAbcAnalyzerFactory : public UFactory
{
    GENERATED_BODY()
public:
    UMyAbcAnalyzerFactory();

    // 仅支持分析，不支持实际创建资产
    virtual UObject* FactoryCreateFile(UClass* InClass, UObject* InParent, FName InName, EObjectFlags Flags, const FString& Filename, const TCHAR* Parms, FFeedbackContext* Warn, bool& bOutOperationCanceled) override;
    virtual bool FactoryCanImport(const FString& Filename) override;
};
```

**MyAbcAnalyzerFactory.cpp**
```cpp
#include "MyAbcAnalyzerFactory.h"
#include "AbcImportSettings.h" // 可能需要访问解析库的类型

UMyAbcAnalyzerFactory::UMyAbcAnalyzerFactory()
{
    SupportedClass = nullptr; // 不创建任何资产类
    bCreateNew = false;
    bEditAfterNew = false;
    bEditorImport = true;
    ImportPriority = -1; // 低优先级，避免干扰真正的导入器
}

bool UMyAbcAnalyzerFactory::FactoryCanImport(const FString& Filename)
{
    return FPaths::GetExtension(Filename).Equals(TEXT("abc"), ESearchCase::IgnoreCase);
}

UObject* UMyAbcAnalyzerFactory::FactoryCreateFile(UClass* InClass, UObject* InParent, FName InName, EObjectFlags Flags, const FString& Filename, const TCHAR* Parms, FFeedbackContext* Warn, bool& bOutOperationCanceled)
{
    // 在此添加你的自定义 Alembic 文件解析逻辑
    // 例如：使用 AlembicLibrary 的底层 API 读取文件头、打印结构信息
    // 这里只是示意
    
    UE_LOG(LogTemp, Display, TEXT("Analyzing Alembic file: %s"), *Filename);
    
    // 不实际导入资产，返回nullptr
    bOutOperationCanceled = false;
    return nullptr;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `AlembicLibrary` | 提供底层的 Alembic 文件解析库 (`libAlembic`) 和核心数据结构（`FAbcImporter`, `FAbcPolyMesh` 等），是 `AlembicImporter` 模块的基础。 |
| `GeometryCache` | 提供 `UGeometryCache` 和 `AGeometryCacheActor` 的运行时支持，是导入几何缓存的目标类型。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复了格式化字符串中位数不匹配导致的潜在问题。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏更新为新的 UE_LOGF 格式，跟进引擎日志系统改进。 |
| 2026-02-27 | `8ce7ca27` | AlembicImporter: Fixed import failure when it couldn't retrieve velocities even though those should | 修复了在无法获取速度数据（理论上应该可以）时导致的导入失败问题。 |
| 2026-02-25 | `74e86b93` | Alembic Import: Fixed out of bouds access (potentially due to negative times). | 修复了由负时间值引起的数组越界访问错误。 |
| 2026-02-03 | `88ba268b` | Fix unreachable code errors | 修复了不可达代码的编译错误。 |

### 维护评价

AlembicImporter 插件目前处于**活跃维护**状态。它从 2022 年从实验性模块转为正式模块，年龄约 4 年，属于引擎中相对成熟的功能。
- **最近更新频率**：在 2026 年 2-4 月有密集的更新，主要集中在**稳定性修复和错误处理**上（如越界访问、导入失败逻辑）。
- **维护状态**：Epic Games 持续对其维护，修复 bug 并跟进引擎基础设施的变更（如日志宏迁移）。没有迹象表明它被废弃。
- **已知限制**：由于 Alembic 格式本身的复杂性和 DCC 工具导出实现的差异，某些复杂的动画或拓扑结构可能仍会出现导入问题。官方文档是解决兼容性问题的首要参考。
- **推荐使用**：**强烈推荐**。对于需要导入外部动画缓存的项目，这是 UE 内置的唯一官方解决方案，功能完整且经过长期迭代，是影视和游戏动画制作管线中的标准工具。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/AlembicImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/AlembicImporter/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/AlembicImporter/Tests)