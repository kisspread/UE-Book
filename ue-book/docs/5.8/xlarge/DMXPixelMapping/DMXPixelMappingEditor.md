# DMX Pixel Mapping Editor

> Tools set for map LED digital pixel strip or fixture arrays regardless of shape or size

| 属性 | 值 |
|---|---|
| 中文名 | DMX 像素映射编辑器 |
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、材质模板） |
| 模块 | `DMXPixelMappingCore` (Runtime), `DMXPixelMappingRuntime` (Runtime), `DMXPixelMappingRenderer` (Runtime), `DMXPixelMappingBlueprintGraph` (Runtime), `DMXPixelMappingEditor` (Runtime), `DMXPixelMappingEditorWidgets` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2021-08-04 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DMX/DMXPixelMapping) | |

## 用途

DMX Pixel Mapping 是一个完整的虚拟制作工具集，用于将 DMX 数据映射到 LED 数字像素灯带或灯具阵列。无论灯带的形状、大小或排列方式如何，都可以通过可视化编辑器将 DMX Fixture Patch 分配到画布上的组件，再由渲染器根据输入纹理（Texture 或 Material）计算每个像素的亮度/颜色，最终通过 DMX 协议输出到真实灯具。

本模块（DMXPixelMappingEditor）是整个插件的**编辑器界面**，提供：
- 可视化设计器（Designer View）：在画布上拖拽、摆放、缩放/旋转输出组件
- 层级视图（Hierarchy View）：树状结构管理组件层次
- DMX 库视图（DMX Library View）：从 DMX Library 选择 Fixture Patch 并添加到映射
- 预览视图（Preview View）：实时预览映射效果
- 布局视图（Layout View）：通过布局脚本自动排列组件
- 属性面板（Details View）：编辑组件属性和输出 DMX 参数

## 使用场景

- 你在搭建 LED 墙体或舞台灯光装置 → 用 DMXPixelMapping 将 Fixture Patch 映射到画布位置
- 你需要把 Texture/Material 的像素亮度映射到 DMX 通道 → 用 Renderer Component 作为输入源
- 你需要管理大型灯阵（如矩阵灯）的像素映射 → 用 Matrix Component + 布局脚本自动排列
- 你需要在编辑器中实时预览 DMX 输出效果 → 用 Preview View 播放 DMX 数据
- 你需要翻转、缩放一组灯具的布局 → 用 Designer View 的 FlipGroup / SizeGroupToTexture

## 蓝图用法

本模块主要是编辑器 UI 逻辑，不暴露 Runtime 蓝图节点。蓝图层面的 DMX 功能由其他模块（DMXPixelMappingRuntime、DMXPixelMappingCore）提供。

### 编辑器内操作

在 DMX Pixel Mapping 编辑器窗口中可执行的操作：

| 操作 | 说明 |
|---|---|
| 添加 Fixture Group | 在 DMX Library View 中创建新的 Fixture Group |
| 添加 Fixture Patch | 从 DMX Library 中选择 Patch 添加到当前 Group |
| 拖放组件 | 从 DMX Library 列表拖放 Patch 到 Designer 画布 |
| 缩放/旋转 | 使用 Transform Handle 调整组件大小和角度 |
| 翻转组 | 水平/垂直翻转 Group 内所有子组件 |
| 适配纹理 | 将 Group 大小调整为与输入纹理一致 |
| 网格吸附 | 开关网格吸附，自定义网格行列数和颜色 |
| 播放/停止 DMX | 编辑器内实时预览 DMX 输出 |

## C++ 用法

### 头文件引入

```cpp
#include "DMXPixelMappingEditorModule.h"
```

### 基本用法 — 获取编辑器工具箱

编辑器通过 `FDMXPixelMappingToolkit` 管理所有视图和选择状态。

```cpp
// 来源: Private/Toolkits/DMXPixelMappingToolkit.h
#include "DMXPixelMappingToolkit.h"

// 初始化编辑器
FDMXPixelMappingToolkit Toolkit;
Toolkit.InitPixelMappingEditor(
    EToolkitMode::Standalone,
    ToolkitHost,
    DMXPixelMappingAsset
);

// 获取各种视图
TSharedRef<SDMXPixelMappingDesignerView> DesignerView = Toolkit.GetOrCreateDesignerView();
TSharedRef<SDMXPixelMappingHierarchyView> HierarchyView = Toolkit.GetOrCreateHierarchyView();
TSharedRef<SDMXPixelMappingDMXLibraryView> LibraryView = Toolkit.GetOrCreateDMXLibraryView();
```

### 基本用法 — 组件选择管理

```cpp
// 来源: Private/Toolkits/DMXPixelMappingToolkit.h

// 获取当前选中的组件
const TSet<FDMXPixelMappingComponentReference>& Selected = Toolkit.GetSelectedComponents();

// 程序化选择组件
TSet<FDMXPixelMappingComponentReference> NewSelection;
NewSelection.Add(Toolkit.GetReferenceFromComponent(SomeComponent));
Toolkit.SelectComponents(NewSelection);

// 检查组件是否被选中
bool bSelected = Toolkit.IsComponentSelected(MyComponent);

// 监听选择变化
Toolkit.GetOnSelectedComponentsChangedDelegate().AddLambda([]()
{
    // 处理选择变化
});
```

### 进阶用法 — View Model 管理 DMX Library

```cpp
// 来源: Private/ViewModels/DMXPixelMappingDMXLibraryViewModel.h

// 创建 ViewModel 管理 DMX Library
UDMXPixelMappingDMXLibraryViewModel* ViewModel = NewObject<UDMXPixelMappingDMXLibraryViewModel>();

// 创建新的 Fixture Group
ViewModel->CreateAndSetNewFixtureGroup(WeakToolkit);

// 添加 Fixture Patch
TArray<UDMXEntityFixturePatch*> Patches;
Patches.Add(MyPatch);
ViewModel->AddFixturePatchesEnsured(Patches);

// 设置是否使用 Patch 颜色
ViewModel->SetNewComponentsUsePatchColor(true);

// 监听 Library 变化
ViewModel->OnDMXLibraryChanged.AddLambda([]()
{
    // Library 已变更
});
```

### 进阶用法 — 布局脚本系统

```cpp
// 来源: Private/ViewModels/DMXPixelMappingLayoutViewModel.h

// 通过 Layout ViewModel 自动排列组件
UDMXPixelMappingLayoutViewModel* LayoutModel = NewObject<UDMXPixelMappingLayoutViewModel>();
LayoutModel->SetToolkit(ToolkitRef);

// 检查是否可以应用布局
if (LayoutModel->CanApplyLayoutScript())
{
    LayoutModel->RequestApplyLayoutScript();  // 下一 tick 应用
    // 或者立即应用
    LayoutModel->ForceApplyLayoutScript();
}

// 监听布局模型变化
LayoutModel->OnModelChanged.AddLambda([]()
{
    // 布局已更新
});
```

## Demo 示例

以下示例演示如何在 C++ 中创建一个自定义的编辑器扩展，监听像素映射的组件变化并执行布局操作。

**PixelMappingEditorExtension.h**

```cpp
#pragma once

#include "CoreMinimal.h"

class FDMXPixelMappingToolkit;

class FPixelMappingEditorExtension
{
public:
    void Initialize(const TSharedRef<FDMXPixelMappingToolkit>& InToolkit);
    void Shutdown();

private:
    void OnSelectedComponentsChanged();
    void AutoArrangeSelectedComponents();

    TWeakPtr<FDMXPixelMappingToolkit> WeakToolkit;
};
```

**PixelMappingEditorExtension.cpp**

```cpp
#include "PixelMappingEditorExtension.h"
#include "DMXPixelMappingToolkit.h"
#include "Components/DMXPixelMappingFixtureGroupComponent.h"
#include "Components/DMXPixelMappingMatrixComponent.h"

void FPixelMappingEditorExtension::Initialize(const TSharedRef<FDMXPixelMappingToolkit>& InToolkit)
{
    WeakToolkit = InToolkit;
    InToolkit->GetOnSelectedComponentsChangedDelegate().AddRaw(
        this, &FPixelMappingEditorExtension::OnSelectedComponentsChanged);
}

void FPixelMappingEditorExtension::Shutdown()
{
    if (TSharedPtr<FDMXPixelMappingToolkit> Toolkit = WeakToolkit.Pin())
    {
        Toolkit->GetOnSelectedComponentsChangedDelegate().RemoveAll(this);
    }
    WeakToolkit.Reset();
}

void FPixelMappingEditorExtension::OnSelectedComponentsChanged()
{
    AutoArrangeSelectedComponents();
}

void FPixelMappingEditorExtension::AutoArrangeSelectedComponents()
{
    TSharedPtr<FDMXPixelMappingToolkit> Toolkit = WeakToolkit.Pin();
    if (!Toolkit.IsValid())
    {
        return;
    }

    const TSet<FDMXPixelMappingComponentReference>& Selected = Toolkit->GetSelectedComponents();
    if (Selected.Num() == 0)
    {
        return;
    }

    // 获取第一个选中的 Fixture Group
    UDMXPixelMappingFixtureGroupComponent* GroupComp = Toolkit->GetFixtureGroupFromSelection();
    if (!GroupComp)
    {
        return;
    }

    // 使用翻转命令调整布局
    Toolkit->FlipGroup(Orient_Horizontal, true);
}
```

## 模块依赖

本模块依赖其他 DMX 相关模块和标准 UE 编辑器模块。

| 模块 | 用途 |
|---|---|
| `DMXPixelMappingCore` | 核心数据类型（Fixture Group、Matrix、输出组件等） |
| `DMXPixelMappingRuntime` | 运行时像素映射逻辑 |
| `DMXPixelMappingRenderer` | 渲染器组件，处理输入纹理到 DMX 的转换 |
| `DMXPixelMappingBlueprintGraph` | 蓝图图节点支持 |
| `DMXPixelMappingEditorWidgets` | 编辑器专用 Widget |
| `DMX` | DMX 协议和 Fixture Patch 核心模块 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `5f2a2a90` | DMX - Fix a crash when pixel mapping has unpatched components and draws patch colors | 修复未分配 Patch 的组件绘制颜色时崩溃的问题 |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 重构视口客户端关联/解除关联的通知机制 |
| 2026-05-14 | `9144f8ac` | [Backout] - CL53913857 | 回退 CL53913857 的改动 |
| 2026-05-14 | `9ede83f2` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 视口客户端关联通知的另一处重构 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 常量截断为 float 的警告 |

### 维护评价

- **活跃维护**：最近更新在 2026 年 5 月，有实质性 bug 修复和代码重构
- **成熟度**：自 2021 年创建以来持续迭代，已具备完整的编辑器功能集
- **代码质量**：采用 MVVM 架构（ViewModel/View 分离），支持 Undo/Redo，有完整的拖放系统
- **已知限制**：所有模块均标记为 Runtime 类型（可能是 DMX 系统的特殊需求，因为运行时也需要部分编辑器功能）

**推荐使用**：✅ 强烈推荐。这是 Epic 官方维护的虚拟制作核心工具，功能完整，持续更新，适合任何需要 DMX 像素映射的虚拟制片场景。

## 编辑器架构概览

本模块采用 MVVM 架构模式：

```
┌─────────────────────────────────────────────┐
│              FDMXPixelMappingToolkit         │  ← 编辑器主控（AssetEditorToolkit）
│  管理选择、命令、所有视图的生命周期            │
├─────────────────────────────────────────────┤
│  Views（视图层）                              │
│  ├─ SDMXPixelMappingDesignerView            │  ← 画布设计器
│  ├─ SDMXPixelMappingHierarchyView           │  ← 组件层级树
│  ├─ SDMXPixelMappingDMXLibraryView          │  ← DMX 库选择器
│  ├─ SDMXPixelMappingPreviewView             │  ← 实时预览
│  ├─ SDMXPixelMappingDetailsView             │  ← 属性面板
│  └─ SDMXPixelMappingLayoutView              │  ← 布局脚本
├─────────────────────────────────────────────┤
│  ViewModels（视图模型层）                     │
│  ├─ UDMXPixelMappingDMXLibraryViewModel     │  ← DMX 库数据管理
│  ├─ UDMXPixelMappingLayoutViewModel         │  ← 布局脚本管理
│  ├─ FDMXPixelMappingOutputComponentModel    │  ← 输出组件显示逻辑
│  └─ FDMXPixelMappingHierarchyItem           │  ← 层级树节点模型
├─────────────────────────────────────────────┤
│  Widgets（自定义控件）                        │
│  ├─ SDMXPixelMappingSurface                 │  ← 缩放/平移基础画布
│  ├─ SDMXPixelMappingTransformHandle         │  ← 缩放/旋转拖拽手柄
│  ├─ SDMXPixelMappingRuler                   │  ← 标尺
│  └─ SDMXPixelMappingZoomPan                 │  ← 缩放平移容器
└─────────────────────────────────────────────┘
```

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DMX/DMXPixelMapping)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/dmx-pixel-mapping-in-unreal-engine/)