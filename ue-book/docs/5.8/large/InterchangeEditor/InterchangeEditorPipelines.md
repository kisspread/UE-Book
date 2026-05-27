# Interchange Editor Pipelines

> The Interchange Editor plugin exposes the Interchange import framework and pipelines to Unreal Editor.

| 属性 | 值 |
|---|---|
| 中文名 | 导入框架管线模块 |
| 分类 | Importers |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `InterchangeEditorPipelines` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2021-10-12 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange/Editor/Source/Pipelines) | |

## 用途

InterchangeEditorPipelines 是 Interchange 导入框架在编辑器侧的**管线（Pipeline）管理系统**。它解决的核心问题是：当用户通过编辑器导入资产（FBX、glTF、MaterialX 等）时，如何让用户可视化地配置、选择、组合和调试导入管线。

具体功能包括：

- **管线配置对话框**：提供 `SInterchangePipelineConfigurationDialog` UI，让用户在导入前预览源文件内容、选择管线栈（Pipeline Stack）、调整管线参数
- **场景图检查器**：通过 `SInterchangeGraphInspectorWindow` 展示源文件解析后的节点树（BaseNodeContainer），支持按节点层级选择性导入
- **资产卡片视图**：`SInterchangeAssetCard` 以卡片形式展示每种资产类型（静态网格、骨骼网格、材质等）的导入状态和数量
- **编辑器蓝图管线基类**：`UInterchangeEditorPipelineBase` / `UInterchangeEditorBlueprintPipelineBase` 允许用户创建编辑器专用的蓝图管线
- **管线资产工厂**：为 Blueprint Pipeline、Python Pipeline 等自定义管线类型提供资产创建入口
- **属性面板自定义**：`FInterchangePipelineBaseDetailsCustomization` 和 `FInterchangeBaseNodeDetailsCustomization` 自定义管线和节点在 Details 面板中的显示方式，支持冲突信息展示和各类属性类型的编辑控件

简言之，这个模块是 Interchange 导入流程的**编辑器 UI 层**，将底层导入框架的能力暴露给用户进行交互式操作。

## 使用场景

- 你在编辑器中导入 FBX/glTF 文件 → 弹出管线配置对话框，调整导入参数后导入
- 你需要只导入源文件中的部分网格或材质 → 使用场景图检查器（Graph Inspector）勾选目标节点
- 你要批量导入多种资产类型但想分别控制每种类型的开关 → 使用资产卡片视图（Asset Cards）按类型启用/禁用
- 你需要自定义导入管线逻辑 → 基于 `UInterchangeEditorBlueprintPipelineBase` 创建蓝图管线资产
- 你想在蓝图或 Python 中完全控制导入行为 → 创建 Python Pipeline 资产并关联到导入流程
- 你要调试某个 glTF 或 MaterialX 文件的解析结果 → 打开 Graph Inspector 查看节点树和属性

## 蓝图用法

### 核心类

| 类 | 说明 |
|---|---|
| `UInterchangeEditorPipelineBase` | 编辑器专用管线基类，蓝图管线应继承此类 |
| `UInterchangeEditorBlueprintPipelineBase` | 编辑器蓝图管线的蓝图基类，用于在编辑器中创建自定义管线 |
| `UInterchangePipelineConfigurationGeneric` | 通用管线配置类，控制导入对话框的显示 |
| `UInterchangeGraphInspectorPipeline` | 场景图检查器专用管线，不可重导入 |
| `UInterchangeCardsPipeline` | 资产卡片管线，控制工厂节点的启用/禁用 |

### 创建自定义编辑器蓝图管线

1. 在 Content Browser 中右键 → **Interchange** → **Interchange Blueprint** → **Interchange Editor Blueprint Pipeline**
2. 蓝图编辑器中，父类默认为 `UInterchangeEditorPipelineBase`
3. 重写 `ExecutePipeline` 事件，添加自定义处理逻辑
4. 在导入对话框中即可选择该自定义管线

### 使用管线配置对话框

管线配置对话框由 `UInterchangePipelineConfigurationGeneric::ShowPipelineDialog_Internal` 触发，通常在以下场景自动弹出：

- 拖放文件到 Content Browser
- 使用 File → Import 菜单导入资产
- 重新导入已有资产时选择"显示导入选项"

对话框内用户可以：
- 从下拉框切换不同的 **Pipeline Stack 预设**
- 在左侧列表中选择具体管线并修改其参数
- 使用 **Asset Cards** 切换各类资产的导入开关
- 点击 **Preview Import** 预览导入结果
- 勾选 **Use Same Settings For All** 统一所有管线设置

## C++ 用法

### 头文件引入

```cpp
#include "InterchangeEditorPipelinesModule.h"
#include "InterchangeEditorBlueprintPipelineBase.h"
```

### 检查模块可用性

```cpp
if (IInterchangeEditorPipelinesModule::IsAvailable())
{
    IInterchangeEditorPipelinesModule& Module = IInterchangeEditorPipelinesModule::Get();
    // 模块已加载，可以安全使用
}
```

### 创建编辑器专用蓝图管线

```cpp
#include "InterchangeEditorBlueprintPipelineBase.h"

// UInterchangeEditorPipelineBase 是编辑器专用管线基类
// 在 C++ 中继承它来创建纯 C++ 编辑器管线
UCLASS()
class UMyCustomEditorPipeline : public UInterchangeEditorPipelineBase
{
    GENERATED_BODY()

public:
    virtual void ExecutePipeline(
        UInterchangeBaseNodeContainer* BaseNodeContainer,
        const TArray<UInterchangeSourceData*>& SourceDatas,
        const FString& ContentBasePath) override
    {
        // 自定义管线逻辑
        // 遍历 BaseNodeContainer 中的节点，修改属性或过滤节点
        
        Super::ExecutePipeline(BaseNodeContainer, SourceDatas, ContentBasePath);
    }

    // 编辑器管线不支持重导入（根据需求可覆盖）
    virtual bool SupportReimport() const override { return false; }
};
```

### 禁用特定工厂节点类（Cards Pipeline 用法）

```cpp
#include "InterchangeCardsPipeline.h"

// UInterchangeCardsPipeline 用于批量控制哪些资产类型参与导入
UInterchangeCardsPipeline* CardsPipeline = GetCardsPipeline();

TArray<UClass*> DisabledClasses;
DisabledClasses.Add(USkeletalMesh::StaticClass());
DisabledClasses.Add(UMaterialInstance::StaticClass());

CardsPipeline->SetDisabledFactoryNodes(DisabledClasses);
// 后续执行管线时，这些类型的资产将不会被导入
```

### 自定义管线属性面板

```cpp
#include "InterchangeEditorPipelineDetails.h"

// 注册自定义 Detail 定制化
FPropertyEditorModule& PropertyModule = 
    FModuleManager::LoadModuleChecked<FPropertyEditorModule>("PropertyEditor");

PropertyModule.RegisterCustomClassLayout(
    UMyPipeline::StaticClass()->GetFName(),
    FOnGetDetailCustomizationInstance::CreateStatic(
        &FInterchangePipelineBaseDetailsCustomization::MakeInstance));
```

## Demo 示例

### 最小编辑器蓝图管线（C++ 版）

**MyEditorPipeline.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "InterchangeEditorBlueprintPipelineBase.h"
#include "MyEditorPipeline.generated.h"

UCLASS(BlueprintType, Blueprintable)
class MYPROJECT_API UMyEditorPipeline : public UInterchangeEditorPipelineBase
{
    GENERATED_BODY()

public:
    UMyEditorPipeline();

    // 重写管线执行逻辑
    virtual void ExecutePipeline(
        UInterchangeBaseNodeContainer* BaseNodeContainer,
        const TArray<UInterchangeSourceData*>& SourceDatas,
        const FString& ContentBasePath) override;

    /** 是否支持重导入 */
    virtual bool SupportReimport() const override { return true; }

    // 自定义管线属性：控制是否导入动画
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Import Options")
    bool bImportAnimations = true;

    // 自定义管线属性：统一缩放
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Import Options")
    float UniformScale = 1.0f;
};
```

**MyEditorPipeline.cpp**
```cpp
#include "MyEditorPipeline.h"
#include "InterchangeImportDefinitions.h"

UMyEditorPipeline::UMyEditorPipeline()
{
    // 设置管线显示名称
    PipelineDisplayName = TEXT("My Custom Editor Pipeline");
}

void UMyEditorPipeline::ExecutePipeline(
    UInterchangeBaseNodeContainer* BaseNodeContainer,
    const TArray<UInterchangeSourceData*>& SourceDatas,
    const FString& ContentBasePath)
{
    // 必须先调用父类
    Super::ExecutePipeline(BaseNodeContainer, SourceDatas, ContentBasePath);

    if (!bImportAnimations)
    {
        // 遍历所有节点，移除动画相关节点
        TArray<UInterchangeBaseNode*> AllNodes;
        BaseNodeContainer->GetNodes(AllNodes);

        for (UInterchangeBaseNode* Node : AllNodes)
        {
            if (Node && Node->GetTypeName() == TEXT("Animation"))
            {
                BaseNodeContainer->RemoveNode(Node->GetUniqueID());
            }
        }
    }

    // UniformScale 可通过修改节点属性来应用
    if (!FMath::IsNearlyEqual(UniformScale, 1.0f))
    {
        TArray<UInterchangeBaseNode*> MeshNodes;
        BaseNodeContainer->GetNodes(MeshNodes);
        
        for (UInterchangeBaseNode* Node : MeshNodes)
        {
            // 在节点上设置缩放因子（具体属性名取决于管线实现）
            // 此处为示意代码
        }
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `InterchangeImport` | 核心导入框架，提供 Pipeline、Translator、NodeContainer 等基础设施 |
| `InterchangeCore` | 节点容器、属性系统等核心类型 |
| `InterchangeFactoryNodes` | 工厂节点类型定义 |

无其他特殊依赖（仅标准 Core/Engine/Slate 等）。

> **注意**：实际 Build.cs 中的依赖需要查看 `Source/Pipelines/InterchangeEditorPipelines.Build.cs` 确认，以上为基于头文件引用推断的关键依赖。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `099f7387` | [Interchange] Animation frame alignment and glTF translator frame aligner removed. | 移除动画帧对齐和 glTF 翻译器帧对齐器 |
| 2026-04-22 | `cc360b1e` | Add accessor to InterchangeEditorScriptLibrary that returns actors in a level instance without loading | 添加脚本库接口，无需加载即可返回关卡实例中的 Actor |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 日志宏迁移到 UE_LOGF 格式 |
| 2026-04-13 | `05458c60` | [Interchange] Reworking Static and Skeletal Mesh import settings | 重构静态网格和骨骼网格的导入设置 |
| 2026-04-13 | `05458c60` | [Interchange] Reworking Static and Skeletal Mesh import settings | 重构静态网格和骨骼网格的导入设置 |

### 维护评价

- **活跃维护**：最近 6 个月内有多次实质性更新，包括功能重构（网格导入设置）、API 改进（脚本库访问器）和框架清理（移除帧对齐器）
- Interchange 是 Epic 重点推进的下一代资产导入框架，作为替代传统 FBX Importer 的方案，持续受到投入
- 编辑器管线模块是 Interchange 用户交互的核心层，预计会长期维护
- 该模块与 UE5 的版本迭代同步更新，无废弃迹象
- **推荐使用**：如果你正在开发基于 Interchange 的自定义导入流程，此模块是必不可少的

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange/Editor/Source/Pipelines)
- 官方文档：无（.uplugin 中 DocsURL 为空）
- 父插件：[Interchange Editor](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange/Editor)
- 核心框架：[Interchange Import](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange/Import)