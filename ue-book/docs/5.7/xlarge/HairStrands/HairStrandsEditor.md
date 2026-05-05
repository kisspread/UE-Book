# Groom (HairStrands)

> Rendering and simulation of grooms

| 属性 | 值 |
|---|---|
| 分类 | Geometry |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（图标、材质模板等） |
| 模块 | `HairStrandsCore` (Runtime), `HairCardGeneratorFramework` (Runtime), `HairStrandsDataflow` (Runtime), `HairStrandsDeformer` (Runtime), `HairStrandsEditor` (Runtime), `HairStrandsRuntime` (Runtime), `HairStrandsSolver` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-08-02 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/HairStrands) | |

## 用途

HairStrands（Groom）插件是 UE5 中用于**毛发/发型（Groom）资产的导入、编辑、渲染和物理模拟**的完整解决方案。它解决了以下核心问题：

- **毛发资产导入**：支持从 Alembic (.abc) 等外部格式导入基于 Strand（发丝）的毛发数据，包括引导曲线（guides）和渲染曲线（strands）
- **毛发渲染**：通过 Strands-based rendering 实现高质量的实时毛发渲染，支持 LOD、透明度排序、光照等
- **毛发物理模拟**：基于引导曲线的实时物理模拟，支持碰撞、风力、重力等交互
- **Groom Cache**：支持导入和播放预烘焙的毛发动画缓存
- **Groom Binding**：将毛发资产绑定到骨骼网格体（SkeletalMesh），使毛发跟随角色骨骼运动
- **Hair Cards 生成**：将 Strand-based 毛发转换为 Hair Cards（片状毛发），用于性能优化
- **Dataflow 集成**：通过 Dataflow 图编辑器对毛发数据进行程序化处理

该插件默认不启用（`EnabledByDefault: false`），需要在项目设置中手动开启。它包含 7 个运行时模块，覆盖从核心数据、物理求解、渲染、变形器到编辑器工具的完整管线。

## 使用场景

- 你在制作写实角色，需要基于发丝的高质量毛发渲染 → 启用 HairStrands，导入 Alembic Groom 资产
- 你需要毛发随角色骨骼动画实时物理摆动 → 使用 Groom Binding + HairStrandsSolver 模拟
- 你有预烘焙的毛发动画序列 → 导入 Groom Cache 播放
- 你需要在低端平台上使用毛发 → 使用 HairCardGenerator 将 Strand 转换为 Hair Cards
- 你需要程序化处理毛发数据（重拓扑、LOD 生成等）→ 使用 HairStrandsDataflow 模块
- 你需要自定义毛发变形效果 → 使用 HairStrandsDeformer 模块

## 蓝图用法

HairStrandsEditor 模块主要提供编辑器侧的资产导入、编辑器 UI 和工具，运行时蓝图 API 主要分布在 HairStrandsCore 和 HairStrandsRuntime 模块中。以下是从编辑器模块提取的关键功能：

### 核心资产类型

| 资产类型 | 说明 | 编辑器分类 |
|---|---|---|
| `UGroomAsset` | 毛发资产，包含发丝几何数据和材质 | Physics |
| `UGroomBindingAsset` | 毛发绑定资产，将 Groom 绑定到 SkeletalMesh | Misc |
| `UGroomCache` | 毛发动画缓存资产 | Misc |

### 编辑器命令

| 命令 | 说明 | 所在类 |
|---|---|---|
| `BeginHairPlaceTool` | 启动毛发放置工具 | `FGroomEditorCommands` |
| `ResetSimulation` | 重置毛发模拟 | `FGroomEditorCommands` |
| `PauseSimulation` | 暂停毛发模拟 | `FGroomEditorCommands` |
| `PlaySimulation` | 播放毛发模拟 | `FGroomEditorCommands` |
| `PlayAnimation` | 播放动画 | `FGroomEditorCommands` |
| `StopAnimation` | 停止动画 | `FGroomEditorCommands` |
| `Simulate` | 执行模拟 | `FGroomEditorCommands` |
| `LODAuto` | 自动 LOD | `FGroomViewportLODCommands` |
| `LOD0` | 强制 LOD 0 | `FGroomViewportLODCommands` |

### Dataflow 模板管理

| 函数 | 说明 | 所在类 |
|---|---|---|
| `RegisterGroomDataflowTemplate` | 注册 Dataflow 模板 | `UE::Groom` (命名空间) |
| `UnregisterGroomDataflowTemplate` | 注销 Dataflow 模板 | `UE::Groom` |
| `RegisterGroomDataflowTemplatePath` | 注册模板路径（动态加载） | `UE::Groom` |
| `BuildGroomDataflowAsset` | 从模板构建 Dataflow 资产 | `UE::Groom` |

### 使用示例（蓝图描述）

1. **导入 Groom 资产**：在 Content Browser 中右键 → Import，选择 .abc 文件 → 在导入对话框中配置 Groom Import Options → 生成 UGroomAsset
2. **创建 Groom Binding**：右键创建 GroomBinding 资产 → 选择源 Groom 和目标 SkeletalMesh → 生成绑定数据
3. **预览毛发**：双击 Groom Asset 打开 Groom Editor → 使用视口中的 LOD 切换和模拟控制按钮预览效果
4. **放置毛发到场景**：使用 `BeginHairPlaceTool` 命令进入毛发放置模式，在场景中放置 Groom Actor

## C++ 用法

### 头文件引入

```cpp
#include "HairStrandsImporter.h"
#include "GroomCacheImporter.h"
#include "HairStrandsFactory.h"
#include "HairStrandsTranslator.h"
```

### 基本用法 — 导入 Groom 资产

从 `FHairStrandsImporter` 的接口提取：

```cpp
#include "HairStrandsImporter.h"
#include "GroomImportOptions.h"

// 创建导入上下文
UGroomImportOptions* ImportOptions = NewObject<UGroomImportOptions>();
FHairImportContext ImportContext(ImportOptions, GetTransientPackage(), UGroomAsset::StaticClass(), 
    FName("MyGroom"), RF_NoFlags);

// 准备 HairDescription（通常由 Translator 生成）
FHairDescription HairDescription;
// ... 填充 HairDescription 数据 ...

// 导入为 GroomAsset
UGroomAsset* GroomAsset = FHairStrandsImporter::ImportHair(ImportContext, HairDescription);
```

来源：`Engine/Plugins/Runtime/HairStrands/Source/HairStrandsEditor/Public/HairStrandsImporter.h`

### 基本用法 — 自定义文件翻译器

```cpp
#include "HairStrandsTranslator.h"

class FMyCustomGroomTranslator : public IGroomTranslator
{
public:
    virtual bool Translate(const FString& FilePath, FHairDescription& OutHairDescription, 
                           const FGroomConversionSettings& ConversionSettings) override
    {
        // 解析自定义文件格式，填充 HairDescription
        // ...
        return true;
    }

    virtual bool CanTranslate(const FString& FilePath) override
    {
        // 检查文件是否可以被翻译
        return FilePath.EndsWith(TEXT(".myformat"));
    }

    virtual bool IsFileExtensionSupported(const FString& FileExtension) const override
    {
        return FileExtension == TEXT("myformat");
    }

    virtual FString GetSupportedFormat() const override
    {
        return TEXT("myformat;My Custom Groom Format");
    }
};
```

来源：`Engine/Plugins/Runtime/HairStrands/Source/HairStrandsEditor/Public/HairStrandsTranslator.h`

### 进阶用法 — 注册自定义翻译器

```cpp
#include "HairStrandsEditor.h"

// 在模块 StartupModule 中注册
void FMyModule::StartupModule()
{
    FGroomEditor::Get().RegisterHairTranslator<FMyCustomGroomTranslator>();
}
```

来源：`Engine/Plugins/Runtime/HairStrands/Source/HairStrandsEditor/Public/HairStrandsEditor.h`

### 进阶用法 — 导入 Groom Cache

```cpp
#include "GroomCacheImporter.h"
#include "HairStrandsTranslator.h"

// 获取翻译器
TSharedPtr<IGroomTranslator> Translator = MakeShared<FMyCustomGroomTranslator>();

// 准备动画信息
FGroomAnimationInfo AnimInfo;
// ... 设置帧率、帧数等 ...

// 创建导入上下文
FHairImportContext HairImportContext(ImportOptions);

// 导入 Groom Cache
TArray<UGroomCache*> Caches = FGroomCacheImporter::ImportGroomCache(
    TEXT("/path/to/file.abc"),
    Translator,
    AnimInfo,
    HairImportContext,
    GroomAssetForCache,
    EGroomCacheImportType::None
);
```

来源：`Engine/Plugins/Runtime/HairStrands/Source/HairStrandsEditor/Public/GroomCacheImporter.h`

### 进阶用法 — Dataflow 模板管理

```cpp
#include "HairStrandsFactory.h"

// 注册自定义 Dataflow 模板
UE::Groom::FGroomDataflowTemplateData TemplateData;
TemplateData.TemplateName = TEXT("MyCustomTemplate");
TemplateData.TemplateTitle = TEXT("Custom Groom Processing");
TemplateData.TemplateTooltip = TEXT("Process groom data with custom logic");
TemplateData.TemplatePath = TEXT("/Game/Dataflow/MyGroomDataflow");
TemplateData.bIsPrimaryTemplate = true;

UE::Groom::RegisterGroomDataflowTemplate(TemplateData);

// 也可以注册模板路径，支持动态加载
UE::Groom::RegisterGroomDataflowTemplatePath(TEXT("/Game/Dataflow/Templates"));

// 为 Groom 资产构建 Dataflow 资产
bool bSuccess = UE::Groom::BuildGroomDataflowAsset(GroomAsset);
```

来源：`Engine/Plugins/Runtime/HairStrands/Source/HairStrandsEditor/Public/HairStrandsFactory.h`

## Demo 示例

### 自定义 Groom 翻译器模块

```cpp
// MyGroomTranslator.h
#pragma once

#include "HairStrandsTranslator.h"

class FMyGroomTranslator : public IGroomTranslator
{
public:
    virtual bool Translate(const FString& FilePath, FHairDescription& OutHairDescription,
                           const FGroomConversionSettings& ConversionSettings) override;
    virtual bool CanTranslate(const FString& FilePath) override;
    virtual bool IsFileExtensionSupported(const FString& FileExtension) const override;
    virtual FString GetSupportedFormat() const override;
};
```

```cpp
// MyGroomTranslator.cpp
#include "MyGroomTranslator.h"
#include "HairDescription.h"

bool FMyGroomTranslator::Translate(const FString& FilePath, FHairDescription& OutHairDescription,
                                     const FGroomConversionSettings& ConversionSettings)
{
    // 读取自定义格式文件
    TArray<uint8> FileData;
    if (!FFileHelper::LoadFileToArray(FileData, *FilePath))
    {
        return false;
    }

    // 解析文件数据并填充 HairDescription
    // OutHairDescription.SetNumPositions(...);
    // OutHairDescription.SetPosition(Index, FVector(...));
    // ...

    return true;
}

bool FMyGroomTranslator::CanTranslate(const FString& FilePath)
{
    return FilePath.EndsWith(TEXT(".mygroom"));
}

bool FMyGroomTranslator::IsFileExtensionSupported(const FString& FileExtension) const
{
    return FileExtension == TEXT("mygroom");
}

FString FMyGroomTranslator::GetSupportedFormat() const
{
    return TEXT("mygroom;My Custom Groom Format");
}
```

```cpp
// MyGroomModule.cpp — 注册翻译器
#include "HairStrandsEditor.h"
#include "MyGroomTranslator.h"

class FMyGroomModule : public IModuleInterface
{
public:
    virtual void StartupModule() override
    {
        FGroomEditor::Get().RegisterHairTranslator<FMyGroomTranslator>();
    }
};

IMPLEMENT_MODULE(FMyGroomModule, MyGroomModule);
```

## 模块依赖

HairStrandsEditor 模块的 Build.cs 依赖信息（省略常见依赖）：

| 模块 | 用途 |
|---|---|
| `HairStrandsCore` | Groom 核心数据类型（UGroomAsset、UGroomBindingAsset 等） |
| `HairStrandsRuntime` | 毛发运行时渲染和组件 |
| `HairStrandsSolver` | 毛发物理模拟求解器 |
| `HairStrandsDeformer` | 毛发变形器 |
| `HairStrandsDataflow` | Dataflow 图处理 |
| `HairCardGeneratorFramework` | Hair Cards 生成框架 |

无特殊依赖（仅标准 Core/Engine/Slate 等 + 上述 HairStrands 子模块）。

## 维护状态

### 近期更新

```
- 4ca6edca226e Optional simulation visualisation for strands / Fix bad indexing for custom attributes / update simulation view when asset is changing / Relative offsets for guides LODs
- 8a50bf2b0b0e Use of the groom description source/edit
- 0c3730d24f3f Groom editor : fix crash when changing template within the dataflow editor - Done by preventing the Dataflow editor from being closed and re-opened when the dataflow asset is changed - Simply use the refresh code path the editor already supports
```

- `4ca6edca226e`：多项改进——可选的模拟可视化、修复自定义属性索引错误、资产变更时更新模拟视图、引导曲线 LOD 的相对偏移
- `8a50bf2b0b0e`：使用 groom description 的源/编辑功能
- `0c3730d24f3f`：修复在 Dataflow 编辑器中切换模板时的崩溃问题

### 维护评价

HairStrands（Groom）插件自 2019 年创建以来持续活跃维护，是 UE5 中毛发系统的**核心组件**。从近期 commit 可以看出：

- **活跃维护**：持续有功能性更新和 bug 修复，包括模拟可视化、Dataflow 编辑器稳定性等
- **成熟度高**：已从实验性功能发展为正式的生产级毛发管线，包含 7 个模块覆盖完整工作流
- **默认不启用**：`EnabledByDefault: false`，需要手动在项目设置中启用，说明 Epic 对其稳定性仍保持谨慎态度
- **推荐使用**：对于需要高质量毛发渲染和模拟的项目，这是 UE5 官方推荐的解决方案。建议在启用前评估目标平台的性能需求

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/HairStrands)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/groom-hair-in-unreal-engine/)