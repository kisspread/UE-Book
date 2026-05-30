# SVG Importer

> Importing and handling SVG files（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | SVG 导入器 |
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（运行时模块、编辑器模块） |
| 模块 | `SVGImporter` (Runtime), `SVGImporterEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-09-04 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/SVGImporter) | |

## 用途

SVG Importer 插件解决了将可缩放矢量图形（SVG）文件导入 Unreal Engine 并用于虚拟生产工作流的需求。其核心功能是将二维矢量路径（SVG 的 `<path>`, `<rect>`, `<circle>` 等元素）解析并转换为引擎内的三维动态网格（Dynamic Mesh）或二维纹理（Texture2D）资产。它超越了简单的纹理导入，允许设计师直接将 SVG 设计稿（如 Logo、图标、UI 元素）转化为可在场景中自由调整尺寸、挤出（Extrude）、倒角（Bevel）并应用材质的三维模型，或作为可实时更新的二维纹理使用，极大地提高了虚拟制片和内容创建中矢量资产的工作流效率。

## 使用场景

- 你需要将团队设计的 SVG 格式 Logo 或图标快速转化为三维模型用于虚拟场景。
- 你在构建虚拟制片背景板，需要导入复杂的矢量图形作为前景或装饰元素。
- 你希望有一个 UI 或 HUD 元素能保持矢量清晰度，并能动态调整颜色和样式。
- 你需要将多个 SVG 图形合并或拆分为独立的资产进行更精细的控制。

## 蓝图用法

该插件主要通过 `ASVGActor` 在编辑器和运行时进行交互。大部分属性和操作都在这个 Actor 的蓝图细节面板中暴露。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SVGData` | 指定要导入的 SVG 数据资产 (`USVGData`)。 | `ASVGActor` |
| `RenderMode` | 选择渲染模式：`DynamicMesh3D` (3D网格) 或 `Texture2D` (2D纹理)。 | `ASVGActor` |
| `Scale` | 缩放整个 SVG 图形。 | `ASVGActor` |
| `FillsExtrude` | 控制 SVG 填充区域的挤出深度。 | `ASVGActor` |
| `StrokesExtrude` | 控制 SVG 描边线条的挤出深度。 | `ASVGActor` |
| `StrokesWidth` | 调整描边线条的宽度。 | `ASVGActor` |
| `BevelDistance` | 设置挤出几何体的倒角距离。 | `ASVGActor` |
| `ShapesOffset` | 沿X轴为不同形状应用深度偏移，实现简单的分层效果。 | `ASVGActor` |
| `bSmoothFillShapes` | 是否对填充形状进行平滑处理。 | `ASVGActor` |
| `bIgnoreStrokes` | 是否忽略 SVG 文件中的描边信息。 | `ASVGActor` |
| `BakeToBlueprint` (CallInEditor) | 将当前 SVG Actor 的动态网格烘焙为静态网格，并创建一个包含这些静态网格的蓝图。 | `ASVGActor` |
| `ResetGeometry` (CallInEditor) | 从关联的 SVG Data 重新生成几何体。 | `ASVGActor` |
| `Split` (CallInEditor) | 将此 SVG Actor 拆分为多个 Actor，每个包含一个 SVG 形状组件。 | `ASVGActor` |

### 使用示例（蓝图描述）

1.  **创建并导入 SVG**：
    *   在内容浏览器中右键，选择 `Import` 或使用 `USVGData` 资产类型来导入 `.svg` 文件。
    *   将 `ASVGActor` 拖入场景。
    *   在 Actor 的 `Details` 面板中，将导入的 `USVGData` 资产拖拽到 `SVGData` 属性上。

2.  **调整三维外观**：
    *   确保 `RenderMode` 设置为 `DynamicMesh3D`。
    *   调整 `Scale` 以改变大小。
    *   修改 `FillsExtrude` 和 `StrokesExtrude` 来赋予图形厚度。
    *   设置 `BevelDistance` 来软化边缘。
    *   使用 `ShapesOffset` 来前后移动不同形状，创造深度感。

3.  **烘焙为静态资产**：
    *   调整好所有动态网格参数后，点击 `Details` 面板中的 `Bake To Blueprint` 按钮。
    *   选择保存路径，插件会自动生成静态网格资产、材质和最终蓝图。

## C++ 用法

### 头文件引入

```cpp
#include "SVGImporter/Public/SVGActor.h"
#include "SVGImporter/Public/SVGImporterUtils.h"
#include "SVGImporter/Public/SVGTypes.h"
```

### 基本用法：以 3D 模式创建并配置 SVG Actor

```cpp
// 假设你已经有一个 USVGData* 指针 (MySVGData)
ASVGActor* SVGActor = GetWorld()->SpawnActor<ASVGActor>();
if (SVGActor && MySVGData)
{
    SVGActor->SVGData = MySVGData;
    SVGActor->RenderMode = ESVGRenderMode::DynamicMesh3D;
    SVGActor->SetScale(1.5f);
    SVGActor->SetFillsExtrude(0.2f); // 设置填充挤出为 0.2 个单位
    SVGActor->SetStrokesExtrude(0.1f); // 设置描边挤出为 0.1 个单位
    SVGActor->Initialize(); // 初始化并开始生成网格
}
```

### 进阶用法：程序化操作 SVG 形状并进行烘焙

```cpp
// 程序化获取并修改 SVG 形状的材质
if (ASVGActor* Actor = Cast<ASVGActor>(SomeActor))
{
    // 获取所有填充组件
    TArray<TObjectPtr<USVGFillComponent>> FillComps = Actor->GetFillComponents();
    for (USVGFillComponent* FillComp : FillComps)
    {
        if (FillComp)
        {
            // 动态修改颜色
            FillComp->SetColor(FColor::Red);
        }
    }
}

// 使用工具类将 SVG Actor 烘焙为蓝图资产
if (ASVGActor* ActorToBake = Cast<ASVGActor>(SomeActor))
{
    FString SavePath = TEXT("/Game/SVGAssets/BakedLogo");
    FSVGImporterUtils::BakeSVGActorToBlueprint(ActorToBake, SavePath);
}

// 使用工具类拆分 SVG Actor
if (ASVGActor* ActorToSplit = Cast<ASVGActor>(SomeActor))
{
    ASVGShapesParentActor* ParentActor = FSVGImporterUtils::SplitSVGActor(ActorToSplit);
    // ParentActor 现在包含了多个 ASVGShapeActor 子对象
}
```

## Demo 示例

以下是一个最小化示例，展示如何在 C++ 中生成一个 SVG Actor 并配置其 3D 属性。

**MySVGDemo.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MySVGDemo.generated.h"

class ASVGActor;
class USVGData;

UCLASS()
class AMySVGDemo : public AActor
{
	GENERATED_BODY()

public:
	AMySVGDemo();

	UPROPERTY(EditAnywhere, Category = "SVG")
	TObjectPtr<USVGData> SVGDataAsset;

protected:
	virtual void BeginPlay() override;

private:
	UPROPERTY()
	TObjectPtr<ASVGActor> SpawnedSVGActor;
};
```

**MySVGDemo.cpp**
```cpp
#include "MySVGDemo.h"
#include "SVGImporter/Public/SVGActor.h"
#include "SVGImporter/Public/SVGData.h"

AMySVGDemo::AMySVGDemo()
{
	PrimaryActorTick.bCanEverTick = false;
}

void AMySVGDemo::BeginPlay()
{
	Super::BeginPlay();

	if (SVGDataAsset)
	{
		// 生成 SVG Actor
		SpawnedSVGActor = GetWorld()->SpawnActor<ASVGActor>(GetActorLocation(), GetActorRotation());
		if (SpawnedSVGActor)
		{
			// 配置属性
			SpawnedSVGActor->SVGData = SVGDataAsset;
			SpawnedSVGActor->RenderMode = ESVGRenderMode::DynamicMesh3D;
			SpawnedSVGActor->SetScale(2.0f);
			SpawnedSVGActor->SetFillsExtrude(0.15f);
			SpawnedSVGActor->SetStrokesExtrude(0.08f);
			SpawnedSVGActor->BevelDistance = 0.02f;
			SpawnedSVGActor->bSmoothFillShapes = true;
			// 开始初始化和网格生成
			SpawnedSVGActor->Initialize();
		}
	}
}
```

## 模块依赖

从插件的 `.uplugin` 文件和模块构建文件推断，要使用此插件，你的项目或模块除了依赖标准的 Core、Engine 等模块外，还需确保以下插件可用：

| 模块/插件 | 用途 |
|---|---|
| `GeometryScripting` | 提供对动态网格（Dynamic Mesh）进行几何操作（如挤出、倒角）的基础功能。 |
| `GeometryMask` | 提供基于几何的蒙版功能，可能用于 SVG 元素的裁剪或遮罩。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将传统的 UE_LOG 宏迁移到更现代的 UE_LOGF，是代码规范更新。 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修复一次错误的全局查找替换后的二次修正提交。 |
| 2026-02-27 | `6759aa54` | [Backout] - CL51314860 | 回滚（Backout）了之前的某个代码变更（CL51314860）。 |
| 2026-02-27 | `7723864b` | Move FCoreDelegates::OnPostEngineInit to FCoreDelegates::GetOnPostEngineInit() to fix missing regist... | 修复因委托接口变更导致的注册问题，涉及引擎核心初始化。 |
| 2025-09-04 | `69830deb` | MotionDesign : SVGImporter ... | 插件从 Experimental 目录移至 VirtualProduction 目录的初始提交，标记为 beta 版本。 |

### 维护评价

SVGImporter 是一个相对较新（约1.5年）的插件，并且自首次提交以来，持续有维护性更新。最近的更新（2026年2月和4月）主要集中在内部的编译宏适配和与引擎核心系统的兼容性修复上，表明该插件正在积极维护以适应主引擎分支的变化。然而，其状态仍标记为“Beta”（`IsBetaVersion=true`），且分类为“Experimental”，意味着其 API 可能尚未完全稳定。尽管如此，对于在虚拟生产环境中需要使用矢量图形的项目来说，它是一个功能完整且值得尝试的工具。鉴于其活跃的维护状态和明确的应用场景，**推荐**在评估后使用，但需留意其可能的 API 变动。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/SVGImporter)
- [官方文档]() (当前 .uplugin 中 DocsURL 为空)
- [测试用例]() (未在提供的信息中找到明确的测试文件路径)