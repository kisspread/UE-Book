# Image Plate

> Actor and component types that provide a camera-aligned image plate

| 属性 | 值 |
|---|---|
| 中文名 | 图像板 |
| 分类 | Rendering |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（资产类型：`ImagePlateFileSequence`） |
| 模块 | `ImagePlate` (Runtime), `ImagePlateEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-03-13 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ImagePlate) | |

---

## 用途

`ImagePlate` 插件提供一种始终面向摄像机的 **图像板**（类似广告牌 / 精灵），并支持使用图像序列作为动态纹理源。它常用于以下需求：

- 在场景中放置一个平面，无论摄像机如何旋转，该平面始终保持正对镜头（如电影虚拟背景、UI 元素、公告板等）。
- 播放图像序列动画（如一串连续图片），实现简单的、无需材质的逐帧动画效果。

插件通过 `UImagePlateFileSequence` 资产管理图像序列，通过 `ImagePlate` 组件或 `AImagePlate` Actor 在场景中显示。

**为什么存在？**  
UE5 自带的广告牌组件（`UMaterialBillboard`）需要自定义材质和纹理，对于简单的序列帧播放或单张图片显示较为复杂。`ImagePlate` 提供了开箱即用的组件和资产类型，适合快速搭建面向摄像机的图像显示功能，尤其适用于影视预演、概念演示等实验性场景。

---

## 使用场景

- **电影预演**：在场景中放置角色或道具的平面替代图（如绿幕背景或概念图），始终面向摄像机，方便实时调整构图。
- **UI / 标语**：在游戏世界中显示始终面向玩家的文字或图标，无需使用屏幕空间 UI。
- **简单动画**：使用图像序列实现非循环动画（如爆炸、Logo 展示），无需编写蓝图逻辑管理纹理切换。
- **虚拟演播室**：在摄像机视线方向放置背景板，配合实时合成。

---

## 蓝图用法

> ⚠️ 由于本文档基于提供的 Editor 模块源码，缺少 Runtime 模块的完整公开 API，以下仅列出从资产定义和工厂类推导出的可用蓝图操作。实际可蓝图调用的函数（如 `SetSource`、`SetOpacity` 等）请参考 `AImagePlate` / `UImagePlateComponent` 的蓝图面板。

### 核心节点

当前已知的蓝图可操作内容集中于 **资产创建与配置**，不涉及运行时控制节点（需查看 `ImagePlate` Runtime 模块头文件）。

| 节点 / 属性 | 说明 | 来源 |
|---|---|---|
| `ImagePlateFileSequence`（资产） | 创建一个图像序列资源，指定图片文件路径与帧率 | `UImagePlateFileSequenceFactory` |
| `ImagePlate`（组件） | 添加到 Actor 后，可在细节面板指定 `Source`（纹理或序列） | `UImagePlateComponent`（推断） |
| `ImagePlateActor` | 带有 `ImagePlate` 组件的预设 Actor，可直接拖入场景 | `AImagePlate`（推断） |

### 使用示例（蓝图描述）

1. **创建图像序列资产**  
   在内容浏览器中右键 → `Media` → `Image Plate File Sequence`。命名资产后，双击打开资产标签，在细节面板设置 `File Paths`（支持通配符如 `frame_*.png`）和 `Framerate`。

2. **在场景中使用**  
   从 `Place Actors` 面板拖放 `ImagePlate` Actor 到关卡。选中该 Actor，在细节面板的 `Image Plate` 组件中找到 `Source` 属性，选择上一步创建的序列资产。播放时图像板始终面向摄像机并逐帧播放序列。

3. **运行时动态切换（需使用组件蓝图节点）**  
   假设 `ImagePlate` 组件暴露了 `SetSource(UObject* NewSource)` 蓝图节点，可用于在运行时更换纹理或序列。

---

## C++ 用法

### 头文件引入

```cpp
// 使用 ImagePlate 组件
#include "ImagePlateComponent.h"
// 使用 ImagePlateFileSequence 资产
#include "ImagePlateFileSequence.h"
// 使用工厂创建资产
#include "ImagePlateFileSequenceFactory.h"
```

### 基本用法

**创建 ImagePlateFileSequence 资产**  
通过工厂在 C++ 中创建资产（编辑器模块常用，Runtime 中通常直接加载已有资产）。

```cpp
// 来源：ImagePlateFileSequenceFactory.cpp（推断）
UImagePlateFileSequence* Sequence = NewObject<UImagePlateFileSequence>(
    Package,                                         // 目标包
    UImagePlateFileSequence::StaticClass(),
    TEXT("MyImageSequence"),
    RF_Public | RF_Standalone                        // 标志
);
// 设置帧率与文件列表（属性名根据实际头文件调整）
Sequence->Framerate = 24.0f;
Sequence->PlateTextures = { Texture2D1, Texture2D2, ... }; // 设置纹理数组
```

**在 Actor 中附加 ImagePlate 组件并设置源**  
```cpp
// 来源：典型 Actor 构造函数
AImagePlateActor::AImagePlateActor(const FObjectInitializer& ObjectInitializer)
{
    ImagePlateComponent = CreateDefaultSubobject<UImagePlateComponent>(TEXT("ImagePlate"));
    RootComponent = ImagePlateComponent;
}

// 设置序列
void MyActor::SetSequence(UImagePlateFileSequence* NewSequence)
{
    if (ImagePlateComponent)
    {
        ImagePlateComponent->SetSource(NewSequence); // 假设组件暴露 SetSource
    }
}
```

### 进阶用法

**自定义图像板材质**  
`ImagePlate` 组件通常使用一个默认的材质实例，也可以替换为自定义材质（通过 `ImagePlateComponent->SetMaterial` 或细节面板设置）。

**控制序列播放**  
支持暂停、播放、跳转帧等操作（需查看 `UImagePlateFileSequence` 的蓝图函数，如 `Play()`、`Stop()`、`SetCurrentFrame()`）。

---

## Demo 示例

以下是一个最小化的 Actor 类，演示如何在运行时创建一个图像板并播放序列。

### ImagePlateDemoActor.h
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "ImagePlateDemoActor.generated.h"

class UImagePlateComponent;
class UImagePlateFileSequence;

UCLASS()
class AImagePlateDemoActor : public AActor
{
    GENERATED_BODY()

public:
    AImagePlateDemoActor();

    UFUNCTION(BlueprintCallable, Category = "ImagePlateDemo")
    void SetSequence(UImagePlateFileSequence* Sequence);

protected:
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "ImagePlate")
    UImagePlateComponent* ImagePlateComponent;
};
```

### ImagePlateDemoActor.cpp
```cpp
#include "ImagePlateDemoActor.h"
#include "ImagePlateComponent.h"
#include "ImagePlateFileSequence.h"

AImagePlateDemoActor::AImagePlateDemoActor()
{
    ImagePlateComponent = CreateDefaultSubobject<UImagePlateComponent>(TEXT("ImagePlateComponent"));
    RootComponent = ImagePlateComponent;
}

void AImagePlateDemoActor::SetSequence(UImagePlateFileSequence* Sequence)
{
    if (ImagePlateComponent && Sequence)
    {
        // 假设 UImagePlateComponent 公开了 SetSource(UObject*) 函数
        ImagePlateComponent->SetSource(reinterpret_cast<UObject*>(Sequence));
    }
}
```

> 注意：以上代码依赖于 `UImagePlateComponent` 的实际 API，请查阅官方头文件确认函数签名。

---

## 模块依赖

### 模块一：`ImagePlate` (Runtime)
| 模块 | 用途 |
|---|---|
| 无特殊依赖 | 仅标准 Core/Engine/Slate 等常见依赖 |

### 模块二：`ImagePlateEditor` (Editor)
| 模块 | 用途 |
|---|---|
| 无特殊依赖 | 仅标准 Editor 依赖（UnrealEd, ProjectSettings 等） |

使用时只需保证项目模块依赖 `ImagePlate`（运行时）和 `ImagePlateEditor`（编辑器）。  
示例 `.Build.cs` 片段：
```csharp
PublicDependencyModuleNames.AddRange(new string[] { "ImagePlate" });
if (Target.Type == TargetType.Editor)
{
    PrivateDependencyModuleNames.Add("ImagePlateEditor");
}
```

---

## 维护状态

> 由于提供的 git 历史记录为引擎级全局提交，无法准确判断插件自身的更新频率。以下基于插件创建时间与实验性标记进行分析。

| 维度 | 说明 |
|---|---|
| 创建时间 | 2025-03-13 |
| 最近明显更新 | 无专门针对该插件的提交记录（从提供的历史可见全局性重构） |
| 活跃度判断 | ⚠️ 实验性插件，可能处于初期开发阶段，更新频率未知 |
| 已知限制 | 实验性，API 可能不稳定；只支持编辑器创建资产，Runtime 是否完整待验证 |
| 推荐程度 | 适合快速原型与实验场景，不建议生产项目依赖，除非您接受后续可能的不兼容更改 |

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ImagePlate)
- [官方文档（暂无）]()
- [测试用例（未找到）]()

> 本文档基于 `ImagePlate` 插件 v0.1 生成，部分 API 细节可能存在偏差，请以实际源码为准。