# Composure

> Modern system for real-time compositing. This plugin succeeds legacy Composure and extends CompositeCore.

| 属性 | 值 |
|---|---|
| 中文名 | 现代合成系统 |
| 分类 | Compositing |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器面板 UI、样式资源） |
| 模块 | `Composite` (Runtime), `CompositeEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-09-17 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Compositing/Composite) | |

## 用途

这是一个基于 Unreal Engine 的**实时合成（Compositing）编辑器与运行时系统**，用于在引擎内完成传统后期合成工作流。它替代了旧版 `Composure` 插件，并与 `CompositeCore` 运行时核心配合使用。

该插件解决的核心问题：**在 UE 编辑器中提供完整的实时合成管线管理界面**，包括合成 Actor 的创建与管理、渲染层（Layer）的层级组织、合成通道（Pass）的链式处理、色键（Chroma Key）、色彩校正、遮罩等合成操作。

具体来说，CompositeEditor 模块提供了：
- 一个专用的编辑器面板（Composure Panel），以树状结构展示关卡中所有合成 Actor 及其渲染层
- 针对各种合成层（Plate、阴影反射、平面反射、场景捕获等）的详细属性定制
- 合成通道的过滤、拖拽排序、复制粘贴等管理操作
- 与 Sequencer 的集成，支持对合成层和通道进行关键帧动画
- 色彩校正抽屉（Color Grading Drawer）集成
- 合成网格（Composite Mesh）的可视化叠加管理

## 使用场景

- 你需要在 UE 内进行**实时绿幕/蓝幕抠像合成** → 使用 Composure 的色键 Pass 和 Plate 层
- 你需要将**虚拟场景与实拍素材实时合成** → 使用 Plate 层 + 合成网格 + 遮罩通道
- 你需要对合成素材进行**实时色彩校正** → 使用色度校正 Pass，配合色彩校正抽屉
- 你需要在 Sequencer 中**对合成参数进行关键帧动画** → 使用集成了 Sequencer 对象模式的 Composure 面板
- 你需要管理**阴影、反射等多层合成通道** → 使用阴影反射层、平面反射层等专用层类型

## 蓝图用法

本插件（CompositeEditor）是**纯编辑器模块**，不直接暴露蓝图可调用的运行时 API。其功能通过编辑器 UI 面板和属性定制器（Detail Customization）提供。运行时合成能力由 `CompositeCore` 模块提供。

### 核心编辑器面板

| 功能 | 说明 | 所在类 |
|---|---|---|
| 合成面板 | 管理所有合成 Actor、层和通道的主编辑器面板 | `SCompositeEditorPanel` |
| 层级树视图 | 展示关卡中合成 Actor 及其渲染层的层级结构 | `SCompositePanelLayerTree` |
| 通道树视图 | 展示单个层内所有合成通道的过滤式树状视图 | `SCompositePassTree` |
| Actor 选取器 | 表格形式展示并管理合成 Actor 列表（如合成网格列表） | `SCompositeActorPickerTable` |

### 核心属性定制器

| 定制器 | 说明 | 目标类 |
|---|---|---|
| `FCompositeLayerPlateCustomization` | Plate 层定制：复合网格选择器、媒体纹理、材质自动应用 | `UCompositeLayerPlate` |
| `FCompositePassColorKeyerCustomization` | 色键通道定制：RGB 权重控件、干净底板捕获按钮 | `UCompositePassColorKeyer` |
| `FCompositePassMaskingCustomization` | 遮罩通道定制：遮罩纹理的媒体源选择器 | `UCompositePassMasking` |
| `FCompositeActorCustomization` | 合成 Actor 定制："打开 Composure" 按钮 | `ACompositeActor` |
| `FCompositeSkySphereActorCustomization` | 天穹 Actor 定制：分区过滤、媒体源选择器 | `ACompositeSkySphereActor` |

### 使用示例（编辑器操作）

1. 在编辑器主菜单中打开 **Composure** 面板（通过 `FCompositeEditorModule::RegisterTabSpawners` 注册）
2. 面板左侧显示 **Layer Tree**（层级树），列出关卡中所有 `ACompositeActor` 及其渲染层
3. 选中一个合成 Actor 后，可在右侧 **Details** 面板中编辑其属性
4. 选中一个 Plate 层时，Details 面板会显示 **Composite Mesh** Actor 选取器表格和通道管理面板
5. 可通过 Add 按钮添加新的合成通道（如 Color Keyer、Masking、Color Grading 等）
6. 在通道树中可拖拽排序、复制、粘贴、删除通道
7. 合成面板支持 **Solo**（单独预览）某个层，方便调试
8. 支持 **Pilot Camera**（驾驶相机）到合成 Actor 的相机上，预览合成结果
9. 在 Sequencer 中，合成层和通道会作为 Possessable 子对象显示，可直接关键帧化其属性

## C++ 用法

本模块为编辑器模块，主要供插件内部扩展使用。以下展示关键的扩展点。

### 头文件引入

```cpp
#include "CompositeEditorModule.h"
```

### 基本用法 — 实现自定义通道的 Pass List Owner

`ICompositePassListOwner` 是管理合成通道列表的核心接口，已有两个内置实现：
- `FCompositeLayerPassListOwner`：用于只有单个 `LayerPasses` 数组的标准层
- `FCompositePlatePassListOwner`：用于具有多组 Pass（Layer/Media）的 Plate 层

```cpp
// 来源: Private/UI/CompositePlatePassListOwner.h
// 若需为自定义层创建通道列表管理器，需实现 ICompositePassListOwner
class FMyPassListOwner : public ICompositePassListOwner
{
public:
    virtual bool IsObjectValid() override { return MyLayer.IsValid(); }
    virtual TStrongObjectPtr<UObject> GetObject() override { return TStrongObjectPtr<UObject>(MyLayer.Get()); }
    virtual bool IsPassListPropertyName(const FName& InPropertyName) override 
    { 
        return InPropertyName == GET_MEMBER_NAME_CHECKED(UMyLayer, Passes); 
    }
    virtual int32 GetNumGroups() const override { return INDEX_NONE; } // 无分组
    virtual TArray<TObjectPtr<UCompositePassBase>>& GetPassesForGroup(int32 InGroupIndex) override 
    { 
        return MyLayer->Passes; 
    }
    // ... 其余接口实现
};
```

### 基本用法 — 自定义层属性定制器

```cpp
// 来源: Private/Customizations/CompositeLayerCustomization.h
// 继承 FCompositeLayerCustomization 以获得标准的层属性布局功能
class FMyLayerCustomization : public FCompositeLayerCustomization
{
public:
    static TSharedRef<IDetailCustomization> MakeInstance()
    {
        return MakeShareable(new FMyLayerCustomization());
    }
    
    virtual void CustomizeLayerDetails(IDetailLayoutBuilder& InDetailLayout) override
    {
        // 获取默认的 "Composite" 类别
        IDetailCategoryBuilder& Category = InDetailLayout.EditCategory(TEXT("Composite"));
        
        // 添加默认层属性（跳过 LayerPasses 和自定义隐藏属性）
        AddDefaultLayerProperties(Category);
        
        // 添加通道管理面板（自动隐藏 LayerPasses 数组）
        UMyLayer* Layer = Cast<UMyLayer>(GetCustomizedObject());
        AddPassesGroup(InDetailLayout, Category, Layer);
    }
};
```

### 进阶用法 — Sequencer 对象模式扩展

```cpp
// 来源: Private/Sequencer/CompositeActorObjectSchema.h
// FCompositeActorObjectSchema 将合成 Actor 的层和通道暴露为 Sequencer 中的 Possessable 子对象
// 层级结构: Actor -> Layers (UCompositeLayerBase) -> Passes (UCompositePassBase)

// 该 schema 在 FCompositeEditorModule::OnPostEngineInit 中注册
// 如需扩展自定义合成对象的 Sequencer 集成，可参考其 GetParentObject/GetRelevancy 实现
```

## Demo 示例

以下展示如何注册一个自定义合成层的属性定制器：

```cpp
// MyCompositeLayerCustomization.h
#pragma once

#include "Customizations/CompositeLayerCustomization.h"

class FMyCompositeLayerCustomization : public FCompositeLayerCustomization
{
public:
    static TSharedRef<IDetailCustomization> MakeInstance()
    {
        return MakeShareable(new FMyCompositeLayerCustomization());
    }

    virtual void CustomizeLayerDetails(IDetailLayoutBuilder& InDetailLayout) override;
};
```

```cpp
// MyCompositeLayerCustomization.cpp
#include "MyCompositeLayerCustomization.h"
#include "DetailLayoutBuilder.h"
#include "DetailCategoryBuilder.h"
#include "MyCompositeLayer.h"

void FMyCompositeLayerCustomization::CustomizeLayerDetails(IDetailLayoutBuilder& InDetailLayout)
{
    // 重命名并获取默认的 Composite 类别
    IDetailCategoryBuilder& CompositeCategory = InDetailLayout.EditCategory(
        TEXT("Composite"), 
        FText::GetEmpty(), 
        ECategoryPriority::Important
    );
    
    // 添加默认属性（Name, Enabled, Active 等），排除自定义属性
    AddDefaultLayerProperties(CompositeCategory, {
        GET_MEMBER_NAME_CHECKED(UMyCompositeLayer, CustomParam1),
        GET_MEMBER_NAME_CHECKED(UMyCompositeLayer, CustomParam2)
    });
    
    // 隐藏继承的 LayerPasses 属性并插入通道管理面板
    UMyCompositeLayer* Layer = nullptr;
    // ... 获取当前定制的层对象
    AddPassesGroup(InDetailLayout, CompositeCategory, Layer);
    
    // 在自定义类别中添加特定属性
    IDetailCategoryBuilder& CustomCategory = InDetailLayout.EditCategory(TEXT("Custom Settings"));
    CustomCategory.AddProperty(GET_MEMBER_NAME_CHECKED(UMyCompositeLayer, CustomParam1));
    CustomCategory.AddProperty(GET_MEMBER_NAME_CHECKED(UMyCompositeLayer, CustomParam2));
}
```

注册定制器（在模块启动时）：

```cpp
// FMyModule::StartupModule()
FPropertyEditorModule& PropertyModule = FModuleManager::LoadModuleChecked<FPropertyEditorModule>("PropertyEditor");
PropertyModule.RegisterCustomClassLayout(
    UMyCompositeLayer::StaticClass()->GetFName(),
    FOnGetDetailCustomizationInstance::CreateStatic(&FMyCompositeLayerCustomization::MakeInstance)
);
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Composite` | 合成系统运行时核心，提供 Actor、Layer、Pass 基类 |
| `CompositeCore` | 合成核心运行时库，底层渲染和通道处理 |
| `ColorGradingEditor` | 色彩校正编辑器集成，提供色彩校正抽屉和数据模型 |
| `SequencerCore` / `LevelSequenceEditor` | Sequencer 集成，支持关键帧动画和对象模式 |
| `SceneOutliner` | 场景大纲集成，用于 Actor 选取器中的 Actor 过滤 |
| `EditorWidgets` | 编辑器 UI 组件 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `0d66152d` | Compositing: Add ChromaShift property to compensate for potential chroma subsampling offsets during | 添加色度偏移属性，补偿色度子采样偏移 |
| 2026-05-22 | `90b2a9d0` | Composure: Default bRemoveOverscan to false on Transform2D pass. | Transform2D 通道默认关闭去除过扫描 |
| 2026-05-21 | `e1f95393` | Composure: Release r.Translucency.AutoBeforeDOF / r.Translucency.Holdout.Location override when the | 释放半透明渲染命令行覆盖 |
| 2026-05-20 | `4d6f2665` | Composure: Fixed custom pass pass details view so Interp properties show the keyframe button. | 修复自定义通道详情面板中插值属性的关键帧按钮显示 |
| 2026-05-20 | `de6434f1` | Composure: Add final new icons for composite actors, layers, and passes, and minor tweaks to menu co | 添加合成 Actor/层/通道的最终图标及菜单调整 |

### 维护评价

**积极维护中**。该插件于 2025 年 9 月创建，至今约 1 年，近期（2026 年 5 月）仍有多次实质性功能更新和 bug 修复，表明 Epic 正在积极开发和迭代此插件。

需要注意的事项：
- **Beta 状态**：`.uplugin` 中 `IsBetaVersion: true`，API 可能在未来版本中发生变化
- **默认未启用**：`EnabledByDefault: false`，需要在插件管理器中手动启用
- **旧版 Composure 替代品**：此插件旨在替代旧版 Composure 插件，两者不应同时启用
- **依赖 CompositeCore**：运行时合成能力来自独立的 CompositeCore 模块，本插件主要提供编辑器界面

**推荐使用**：如果你的项目需要实时合成功能，这是一个值得采用的现代解决方案，但需注意其 Beta 状态可能带来的不稳定性。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Compositing/Composite)
- [CompositeCore 源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Compositing/CompositeCore)