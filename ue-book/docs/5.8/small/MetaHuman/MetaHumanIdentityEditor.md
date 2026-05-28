# MetaHuman Identity Editor

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman 身份编辑器 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器资产、UI控件、工厂类） |
| 模块 | `MetaHumanIdentityEditor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 未知 |
| 年龄标签 | 🆕（约 N 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanIdentityEditor) | |

## 用途

`MetaHumanIdentityEditor` 模块是 **MetaHuman Animator 工作流的核心编辑器界面**。它解决的核心问题是：**为艺术家和开发者提供一个完整、可视化的工具链，用于从真实的拍摄素材（如照片或视频）中创建、配置、调整并最终生成可用于 Unreal Engine 的数字人资产（MetaHuman Identity）**。

该模块不仅仅是查看器，而是一个**端到端的工作站**。它整合了面部追踪、姿态管理、曲线编辑、网格体适配（Conforming）、身体定制以及将最终结果转换为可驱动骨骼网格体的全部流程。它通过提供一个专用的编辑器工具包（Toolkit），将 MetaHuman Animator 的核心功能（追踪、求解、适配）与 Unreal Editor 深度集成，使得创建高质量的 MetaHuman 角色变得直观高效。

## 使用场景

- **创建自定义 MetaHuman**：你有演员的头部扫描数据或照片/视频序列，希望基于这些真实数据生成一个独特的 MetaHuman 角色，而不是使用预设库。
- **数字人资产准备**：在影视预演或游戏过场动画中，你需要将特定演员的外貌转化为可驱动的数字人资产。
- **工作流集成**：你的团队已经使用 MetaHuman Animator 生成了追踪数据，现在需要在一个集成的环境中完成剩余的适配、调整和绑定工作。
- **资产迭代与优化**：你已经创建了一个 MetaHuman Identity，但需要调整面部特征、牙齿、身体类型或进行面部精修（Face Refinement）。

## 蓝图用法

本模块主要为**编辑器专用**（Editor-only），其大部分核心功能通过其专用编辑器工具包（`FMetaHumanIdentityAssetEditorToolkit`）和 UI 控件（如 `SMetaHumanIdentityPartsEditor`, `SMetaHumanIdentityPromotedFramesEditor`）暴露，这些类**不是** `BlueprintCallable` 的。因此，其工作流主要在编辑器面板和按钮中完成，而非通过蓝图节点驱动。

### 核心节点

此模块不直接提供 `BlueprintCallable` 节点。与 MetaHuman Identity 的交互主要通过 C++ API 进行。其集成的 UI 功能对应于编辑器中的以下操作：

| 操作 | 对应的编辑器 UI 功能 |
|---|---|
| 添加身份组件 | 点击 “Add” 按钮，选择添加 Face (Neutral/Teeth)、Body 等部件 |
| 设置捕获数据 | 在 “Parts” 面板中选择 Pose，在 Details 面板中指定 Footage 或 Mesh 捕获数据 |
| 管理提升帧 | 使用 “Promoted Frames” 面板添加、选择、删除提升帧 |
| 运行追踪 | 使用工具栏的 “Track Current” 或 “Track All” 按钮 |
| 配置网格体适配 | 使用工具栏的 “Conform” 或 “Mesh To MetaHuman” 按钮 |
| 生成数字人资产 | 完成所有调整后，通过工具栏相关命令生成最终资产 |

## C++ 用法

`MetaHumanIdentityEditor` 模块主要提供编辑器工具类，其公共 API 相对有限，主要用于模块初始化。真正的业务逻辑和数据操作 API 位于 `MetaHumanIdentity` 运行时模块中。

### 头文件引入

```cpp
// 引入编辑器模块（通常不需要直接引入）
#include "MetaHumanIdentityEditorModule.h"

// 引入核心运行时资产类（在你的代码中更常用）
#include "MetaHumanIdentity.h"
```

### 基本用法

此模块的核心是注册编辑器工具包。以下代码展示了该模块在启动和关闭时如何注册和注销其资产类型和属性自定义。

**来源文件:** `Private/MetaHumanIdentityEditorModule.h`

```cpp
// MetaHumanIdentityEditorModule.h 中定义了模块类
class FMetaHumanIdentityEditorModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

private:
    // 用于在关闭时安全注销的缓存名称
    TArray<FName> ClassesToUnregisterOnShutdown;
    FName PropertyToUnregisterOnShutdown;
};
```

### 进阶用法

在 `StartupModule` 中，模块通常会执行以下操作（实现细节未在提供片段中）：

1.  **注册资产定义** (`UAssetDefinition_MetaHumanIdentity`)，使 `UMetaHumanIdentity` 在内容浏览器中可见、可创建、可编辑。
2.  **注册属性自定义** (`FMetaHumanIdentityPoseCustomization`, `FMetaHumanIdentityBodyCustomization` 等)，用于在 Details 面板中定制 `UMetaHumanIdentityPose`、`UMetaHumanIdentityBody` 等对象的显示方式。
3.  **注册自定义资产编辑器** (`UMetaHumanIdentityAssetEditor`)，该编辑器负责创建 `FMetaHumanIdentityAssetEditorToolkit`，即实际的编辑器窗口。

## Demo 示例

以下示例展示了如何以编程方式创建一个 `UMetaHumanIdentity` 资产并对其进行基本操作。请注意，完整的编辑器交互需要在编辑器模块的上下文中进行。

**MyMetaHumanIdentityHelper.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "MyMetaHumanIdentityHelper.generated.h"

class UMetaHumanIdentity;

UCLASS(BlueprintType)
class UMyMetaHumanIdentityHelper : public UObject
{
    GENERATED_BODY()

public:
    // 创建一个新的 MetaHuman Identity 资产
    UFUNCTION(BlueprintCallable, Category = "MetaHuman")
    static UMetaHumanIdentity* CreateIdentity(UObject* Outer, FName Name);

    // 向 Identity 添加一个面部部件
    UFUNCTION(BlueprintCallable, Category = "MetaHuman")
    static bool AddFacePartToIdentity(UMetaHumanIdentity* Identity);
};
```

**MyMetaHumanIdentityHelper.cpp**
```cpp
#include "MyMetaHumanIdentityHelper.h"
#include "MetaHumanIdentity.h"
#include "MetaHumanIdentityPart.h"
#include "MetaHumanIdentityFace.h"
#include "UObject/SavePackage.h"

UMetaHumanIdentity* UMyMetaHumanIdentityHelper::CreateIdentity(UObject* Outer, FName Name)
{
    // 使用工厂模式创建新资产
    UMetaHumanIdentity* NewIdentity = NewObject<UMetaHumanIdentity>(Outer, UMetaHumanIdentity::StaticClass(), Name, RF_Public | RF_Standalone);

    // 保存资产到磁盘（可选）
    if (NewIdentity)
    {
        FString PackagePath = FPackageName::GetLongPackagePath(Outer->GetOutermost()->GetName());
        FString AssetName = Name.ToString();
        FString PackageName = PackagePath / AssetName;

        UPackage* Package = CreatePackage(*PackageName);
        NewIdentity->Rename(*AssetName, Package);
        Package->MarkPackageDirty();

        // 注意：实际保存逻辑更复杂，此处仅为演示
        // FSavePackageArgs SaveArgs;
        // UPackage::SavePackage(Package, NewIdentity, *PackageName, SaveArgs);
    }

    return NewIdentity;
}

bool UMyMetaHumanIdentityHelper::AddFacePartToIdentity(UMetaHumanIdentity* Identity)
{
    if (!Identity)
    {
        return false;
    }

    // 检查是否已存在面部部件
    for (UMetaHumanIdentityPart* Part : Identity->GetParts())
    {
        if (Part && Part->IsA<UMetaHumanIdentityFace>())
        {
            UE_LOG(LogTemp, Warning, TEXT("Identity already has a face part."));
            return false;
        }
    }

    // 创建一个新的面部部件并添加到 Identity
    UMetaHumanIdentityFace* NewFacePart = NewObject<UMetaHumanIdentityFace>(Identity, UMetaHumanIdentityFace::StaticClass(), NAME_None, RF_Transactional);
    Identity->AddPart(NewFacePart);

    return true;
}
```

## 模块依赖

从 `MetaHumanIdentityEditor.Build.cs` 的依赖项推断，要使用此模块的功能，你的模块需要依赖以下独特的模块：

| 模块 | 用途 |
|---|---|
| `MetaHumanIdentity` | 核心运行时资产类 (`UMetaHumanIdentity`, `UMetaHumanIdentityPose` 等) |
| `MetaHumanToolkit` | 提供基础编辑器工具包类 (`FMetaHumanToolkitBase`) |
| `MetaHumanCaptureDataEditor` | 处理捕获数据（视频、网格体）的编辑器部分 |
| `MetaHumanImageViewerEditor` | 提供图像查看器 UI |
| `ControlRigDeveloper` | 与 ControlRig 集成，用于预览和驱动面部 rig |
| `SkeletalMeshUtilitiesCommon` | 提供骨骼网格体相关的通用工具 |
| `MetaHumanSDKEditor` | MetaHuman SDK 的编辑器扩展 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 启用身体追踪时禁用关卡序列导出 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 上的渲染瑕疵 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 身体追踪时过滤可视化对象 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | [MHA] 为现有网格体导出动画序列 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复 Sequencer 缓存问题 |

### 维护评价

- **活跃维护**：基于最近的 Git 提交记录（2026年5月），该模块仍在**积极开发和维护**中。近期的提交主要集中在修复渲染问题、完善身体追踪工作流以及改进与 Sequencer 的集成。
- **核心功能模块**：作为 MetaHuman Animator 工具集的核心编辑器组件，它对于使用 MetaHuman 工作流的用户至关重要，Epic Games 会持续为其提供支持和更新。
- **稳定性与复杂性**：这是一个功能极其丰富且复杂的编辑器模块，涉及众多交互式 UI、3D 视口、追踪算法集成和资产管道。虽然代码量大且更新频繁，但提交信息表明团队正在积极解决已知问题。
- **推荐使用**：如果你的项目需要基于真实数据创建或修改 MetaHuman 角色，**强烈推荐使用此模块**。它是实现该目标的官方和标准方式。对于不需要创建自定义 MetaHuman 的项目，则无需引入此模块。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanIdentityEditor)
- [官方文档]() (无)
- [测试用例]() (未在提供片段中发现明显测试文件路径)