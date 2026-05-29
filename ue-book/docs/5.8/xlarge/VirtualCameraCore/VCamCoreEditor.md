# VirtualCameraCore

> Code for actors, components, and utilities for controlling and viewing cameras via physical devices. See VirtualCamera for content.

| 属性 | 值 |
|---|---|
| 中文名 | 虚拟相机核心 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `DecoupledOutputProvider` (Runtime), `PixelStreamingVCam` (Runtime), `VCamBlueprintNodes` (Runtime), `VCamCore` (Runtime), `VCamCoreEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-01-18 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/VirtualCameraCore) | |

## 用途

VirtualCameraCore 是 Unreal Engine 虚拟制作系统中**虚拟相机功能的核心运行时与编辑器框架**。它为通过物理设备（如 iPad、手机、VR 控制器等）控制和查看 UE 相机提供底层代码支撑，包含 Actor、组件和编辑器工具。

该插件从 `Plugins/Experimental` 迁移而来（CL 30679956, 2024-01-18），标志着虚拟相机功能从实验阶段进入正式支持阶段。它与 `VirtualCamera` 内容插件配合使用——本插件提供代码框架，`VirtualCamera` 提供蓝图资产和具体内容。

**核心设计思想**：将虚拟相机系统拆分为可复用的"修改器"（Modifier）和"连接"（Connection）体系——修改器处理输入和相机控制逻辑，连接负责将数据路由到正确的输出目标，从而实现灵活的虚拟相机配置。

## 使用场景

- 你在做影视虚拟制作，需要通过 iPad 或手机远程控制 Unreal 相机 → 用 VirtualCameraCore
- 你需要自定义相机输入修改器逻辑（如摇臂模拟、稳定器效果）→ 创建自定义 VCamModifier 蓝图
- 你需要通过 Pixel Streaming 将相机视图流式传输到移动设备 → 使用 PixelStreamingVCam 模块
- 你在多用户协作拍摄环境中使用虚拟相机 → 多用户事务过滤确保 VCam 操作不冲突
- 你需要在不同输出目标间切换虚拟相机（如主监视器、流媒体、回放）→ 使用 DecoupledOutputProvider 和连接系统

## 插件模块概览

| 模块 | 类型 | 说明 |
|---|---|---|
| `VCamCore` | Runtime | 虚拟相机核心运行时逻辑：Actor、组件、修改器、连接系统、Widget |
| `VCamCoreEditor` | Runtime | 编辑器工具：属性自定义、资产工厂、蓝图编译验证、多用户支持 |
| `VCamBlueprintNodes` | Runtime | 蓝图自定义节点，用于可视化构建虚拟相机逻辑 |
| `PixelStreamingVCam` | Runtime | Pixel Streaming 集成，将虚拟相机视图流式传输到远程设备 |
| `DecoupledOutputProvider` | Runtime | 解耦输出提供者，支持多目标输出路由 |

---

# VCamCoreEditor 模块

VCamCoreEditor 是 VirtualCameraCore 的编辑器支撑模块。虽然 Build.cs 标记为 Runtime，但实质上是**仅编辑器可用**的模块（依赖 UnrealEd）。

该模块的核心职责：
1. **编辑器属性面板自定义**——为虚拟相机相关属性提供友好的编辑体验
2. **资产创建工厂**——简化 VCam Widget、Modifier 等资产的创建流程
3. **蓝图编译验证**——在编译期检查 Modifier 的输入映射配置正确性
4. **连接目标重映射**——允许开发者自定义 Widget 的连接目标选择界面
5. **多用户编辑支持**——确保虚拟相机操作在协作环境中正确同步

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetAllVCamComponentsInLevel` | 获取关卡中所有已加载的 VCamComponent（排除已销毁、PIE、预览编辑器中的） | `UVCamEditorLibrary` |

### 使用示例

**获取场景中所有虚拟相机组件**：

1. 在蓝图编辑器中搜索 `Get All VCam Components In Level`
2. 将节点拖入图表，输出引脚 `VCamComponents` 连接到数组遍历或 ForEach 循环
3. 用于批量操作所有虚拟相机（如统一切换状态、批量配置等）

```
[Event BeginPlay] → [Get All VCam Components In Level] → [ForEachLoop] → [你的操作逻辑]
```

## C++ 用法

### 头文件引入

```cpp
#include "IVCamCoreEditorModule.h"
#include "IConnectionRemapCustomization.h"
#include "IConnectionRemapUtils.h"
```

### 基本用法

**注册自定义连接目标重映射**（来源：`Public/IVCamCoreEditorModule.h`）

```cpp
// 在编辑器模块的 StartupModule 中注册自定义连接重映射
#include "IVCamCoreEditorModule.h"

// 1. 获取 VCamCoreEditor 模块
IVCamCoreEditorModule& EditorModule = IVCamCoreEditorModule::Get();

// 2. 注册一个针对特定 VCamWidget 子类的自定义重映射
// 只需要为 UMyCustomVCamWidget 提供自定义的连接目标选择界面
EditorModule.RegisterConnectionRemapCustomization(
    UMyCustomVCamWidget::StaticClass(),
    FGetConnectionRemappingCustomization::CreateLambda([]()
    {
        return MakeShared<FMyCustomConnectionRemapCustomization>();
    })
);

// 3. 在 ShutdownModule 中取消注册
EditorModule.UnregisterConnectionRemapCustomization(UMyCustomVCamWidget::StaticClass());
```

### 进阶用法

**实现自定义连接目标重映射**（来源：`Public/IConnectionRemapCustomization.h` + `Public/IConnectionRemapUtils.h`）

```cpp
// 自定义连接目标重映射 - 控制 Widget 在详情面板中如何显示连接设置
class FMyCustomConnectionRemapCustomization : public IConnectionRemapCustomization
{
public:
    // 判断是否为该 Widget 生成自定义连接组
    virtual bool CanGenerateGroup(const FShouldGenerateArgs& Args) const override
    {
        // 仅当 Widget 有效且显示设置匹配时生成
        return Args.CustomizedWidget.IsValid();
    }

    // 自定义详情面板布局
    virtual void Customize(const FConnectionRemapCustomizationArgs& Args) override
    {
        // 使用 Utils 添加连接目标设置到详情面板
        FVCamConnectionTargetSettings NewSettings;
        NewSettings.ConnectionName = "MyConnection";
        
        Args.Utils->AddConnection(FAddConnectionArgs(
            Args.WidgetGroup,
            FName("MyConnection"),
            ConnectionData,
            FOnTargetSettingsChanged::CreateLambda([this, &Args](const FVCamConnectionTargetSettings& InSettings)
            {
                // 当用户在详情面板修改设置时的回调
                // 将新设置写回你的 UPROPERTY
            }),
            Args.Utils->GetRegularFont()
        ));
    }
};
```

**扩展蓝图编译验证**（来源：`Private/Compilation/ModifierCompilationBlueprintExtension.h`）

```cpp
// UModifierCompilationBlueprintExtension 在蓝图编译时自动验证：
// - 检查 Enhanced Input Action 节点引用的 Action 是否存在于 MappingContext 中
// - 缺失的 Action 会产生编译警告
// 
// 这个扩展在蓝图资产加载时自动附加到蓝图，无需手动注册

// 检查蓝图是否需要重新编译以检测问题
bool bNeedsRecompile = UModifierCompilationBlueprintExtension::RequiresRecompileToDetectIssues(MyBlueprint);
```

## Demo 示例

**实现自定义 VCam 连接重映射，为特定 Widget 子类提供连接目标下拉选择**

```cpp
// MyCustomConnectionRemap.h
#pragma once

#include "IConnectionRemapCustomization.h"
#include "VCamWidget.h"

class FMyCustomConnectionRemap : public UE::VCamCoreEditor::IConnectionRemapCustomization
{
public:
    static TSharedRef<IConnectionRemapCustomization> Make()
    {
        return MakeShared<FMyCustomConnectionRemap>();
    }

    virtual bool CanGenerateGroup(
        const UE::VCamCoreEditor::FShouldGenerateArgs& Args) const override;
    
    virtual void Customize(
        const UE::VCamCoreEditor::FConnectionRemapCustomizationArgs& Args) override;

private:
    void OnTargetChanged(
        const FVCamConnectionTargetSettings& NewSettings,
        FName ConnectionName,
        TWeakObjectPtr<UVCamWidget> Widget) const;
};
```

```cpp
// MyCustomConnectionRemap.cpp
#include "MyCustomConnectionRemap.h"
#include "IConnectionRemapUtils.h"

bool FMyCustomConnectionRemap::CanGenerateGroup(
    const UE::VCamCoreEditor::FShouldGenerateArgs& Args) const
{
    // 对所有有效 Widget 生成自定义组
    return Args.CustomizedWidget.IsValid();
}

void FMyCustomConnectionRemap::Customize(
    const UE::VCamCoreEditor::FConnectionRemapCustomizationArgs& Args)
{
    UVCamWidget* Widget = Args.CustomizedWidget.Get();
    if (!Widget)
    {
        return;
    }

    // 遍历 Widget 上所有连接，为每个连接添加目标设置行
    const TArray<FVCamConnection>& Connections = Widget->GetConnections();
    for (const FVCamConnection& Connection : Connections)
    {
        // 添加连接目标设置到详情面板
        Args.Utils->AddConnection(UE::VCamCoreEditor::FAddConnectionArgs(
            Args.WidgetGroup,
            Connection.ConnectionName,
            Connection,
            UE::VCamCoreEditor::FOnTargetSettingsChanged::CreateSP(
                this,
                &FMyCustomConnectionRemap::OnTargetChanged,
                Connection.ConnectionName,
                TWeakObjectPtr<UVCamWidget>(Widget)
            ),
            Args.Utils->GetRegularFont()
        ));
    }
}

void FMyCustomConnectionRemap::OnTargetChanged(
    const FVCamConnectionTargetSettings& NewSettings,
    FName ConnectionName,
    TWeakObjectPtr<UVCamWidget> Widget) const
{
    if (UVCamWidget* W = Widget.Get())
    {
        // 更新 Widget 的连接目标设置
        // 具体实现取决于你的 Widget 子类结构
    }
}
```

**在编辑器模块启动时注册自定义重映射**：

```cpp
// MyEditorModule.cpp (你的编辑器模块)
void FMyEditorModule::StartupModule()
{
    UE::VCamCoreEditor::IVCamCoreEditorModule& VCamEditor = 
        UE::VCamCoreEditor::IVCamCoreEditorModule::Get();
    
    VCamEditor.RegisterConnectionRemapCustomization(
        UMyCustomVCamWidget::StaticClass(),
        UE::VCamCoreEditor::FGetConnectionRemappingCustomization::CreateLambda([]()
        {
            return FMyCustomConnectionRemap::Make();
        })
    );
}

void FMyEditorModule::ShutdownModule()
{
    UE::VCamCoreEditor::IVCamCoreEditorModule& VCamEditor = 
        UE::VCamCoreEditor::IVCamCoreEditorModule::Get();
    
    VCamEditor.UnregisterConnectionRemapCustomization(
        UMyCustomVCamWidget::StaticClass()
    );
}
```

## 模块依赖

`VCamCoreEditor` 模块的 Build.cs 依赖（从源码分析推断）：

| 模块 | 用途 |
|---|---|
| `VCamCore` | 虚拟相机核心运行时模块（UVCamWidget、UVCamComponent、UVCamModifier 等基础类） |
| `EnhancedInput` | 验证修改器蓝图中的 Enhanced Input Action 节点是否与 MappingContext 匹配 |
| `UnrealEd` | 编辑器基础设施（属性自定义、资产工厂、蓝图扩展） |
| `PropertyEditor` | IDetailCustomization、IPropertyTypeCustomization 等详情面板自定义接口 |
| `Concert` / `ConcertSyncCore` | 多用户编辑事务过滤（ShouldObjectBeTransacted） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `876d5541` | Fix the crash with PIE/Simulate | 修复在 PIE/模拟模式下的崩溃问题 |
| 2026-05-12 | `d6533f70` | Virtual Production: Fixed warning regarding EngineAssetDefinitions plugin not being included when it | 修复关于 EngineAssetDefinitions 插件未包含的警告 |
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the | 将虚拟制作资产迁移到不同的资产分类 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到 UE_LOGF |
| 2026-03-09 | `8afaf39f` | Move UVPFullScreenWidget into new non-experimental plugin VirtualProduction/ViewportWidgetOverlay. | 将全屏 Widget 移至独立的非实验性插件 |

### 维护评价

**维护状态：活跃维护中 ✅**

- **创建时间**：2024-01-18（约 2 年前），从 `Experimental` 迁移到正式 `VirtualProduction` 目录
- **更新频率**：最近 3 个月内有多次实质性更新，包括功能迁移、分类调整和崩溃修复
- **活跃度**：Epic Games 团队持续维护，更新集中在 2026 年 3-5 月
- **当前状态**：Beta（`IsBetaVersion: true`），API 可能在后续版本中变化
- **注意事项**：该插件标记为 `EnabledByDefault: false`，需要在项目设置中手动启用
- **推荐使用**：适合虚拟制作项目早期采用，建议关注后续版本的 API 稳定性变化。目前已在 Epic 的虚拟制作工作流中实际使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/VirtualCameraCore)
- 官方文档：无（.uplugin 中 DocsURL 为空）
- 配套内容插件：`Engine/Plugins/VirtualProduction/VirtualCamera`（提供蓝图资产和具体内容）