# MediaViewer

> Media viewer to display and compare media.

| 属性 | 值 |
|---|---|
| 中文名 | 媒体查看器 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（资产配置） |
| 模块 | `MediaViewer` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-09-23 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/MediaViewer) | |

## 用途

MediaViewer 是一个编辑器工具插件，为开发人员提供一个统一的窗口来**浏览、显示和对比多种媒体资源**。它解决以下问题：

- 当你在开发纹理、材质、渲染目标、媒体源或视口内容时，需要实时预览和比较多个图像/视频，默认编辑器只能逐个打开独立窗口，缺少集中管理和对比能力。
- 需要检查纹理的 Mip 级别、像素颜色、缩放、平移等细节，但没有方便的工具。
- 希望将常用的媒体项保存到库（Library）中，分组管理并快速切换。

该插件通过工厂模式支持多种媒体类型（Texture2D、RenderTarget、Material、MediaSource、MediaTexture、场景视口、色块等），并提供 A/B 对比模式、图像状态保存/恢复、历史记录等功能。

## 使用场景

- **美术/技术美术**：对比两张纹理的差异，检查材质渲染结果，查看 RenderTarget 的实时内容。
- **程序员**：调试媒体播放器，对比不同 Mip 级别下的纹理效果，验证视口截图。
- **测试**：快速加载并对比多个媒体资源，验证输出一致性。

## 蓝图用法

该插件是纯编辑器工具，**不提供任何蓝图可调用函数**。所有 API 均为 C++ 接口，用于编辑器模块扩展。

## C++ 用法

### 头文件引入

```cpp
#include "IMediaViewerModule.h"
#include "ImageViewer/IMediaImageViewerFactory.h"
#include "Library/IMediaViewerLibrary.h"
#include "Widgets/IMediaViewerLibraryWidget.h"
```

### 基本用法

**打开默认的 MediaViewer 标签页**（在模块加载后调用）：

```cpp
#include "IMediaViewerModule.h"

void OpenMediaViewer()
{
    IMediaViewerModule& MediaViewerModule = IMediaViewerModule::Get();
    MediaViewerModule.OpenTab();
}
```

**以特定参数打开标签页**（例如禁用侧边栏和工具栏）：

```cpp
UE::MediaViewer::FMediaViewerArgs Args;
Args.bShowSidebar = false;
Args.bShowToolbar = false;
IMediaViewerModule::Get().OpenTab(Args);
```

**注册自定义图像工厂**（用于支持新的媒体类型）：

```cpp
#include "IMediaViewerModule.h"
#include "ImageViewer/IMediaImageViewerFactory.h"

class FMyImageViewerFactory : public UE::MediaViewer::IMediaImageViewerFactory
{
public:
    FMyImageViewerFactory() { Priority = 6000; }

    virtual bool SupportsAsset(const FAssetData& InAssetData) const override { /* 判断 */ }
    virtual TSharedPtr<UE::MediaViewer::FMediaImageViewer> CreateImageViewer(const FAssetData& InAssetData) const override { /* 创建 */ }
    // ... 其他纯虚函数必须实现
};

void RegisterMyFactory()
{
    FName FactoryName = TEXT("MyFactory");
    TSharedRef<FMyImageViewerFactory> Factory = MakeShared<FMyImageViewerFactory>();
    IMediaViewerModule::Get().RegisterFactory(FactoryName, Factory);
}
```

**获取库接口并添加自定义项**：

```cpp
TSharedRef<UE::MediaViewer::IMediaViewerLibrary> Library = IMediaViewerModule::Get().GetLibrary();

// 创建一个简单的颜色项
TSharedRef<UE::MediaViewer::Private::FMediaViewerLibraryItem> ColorItem =
    MakeShared<UE::MediaViewer::Private::FColorImageViewer::FItem>(
        FText::FromString("MyColor"),
        FText::GetEmpty(),
        false,
        FLinearColor::Red
    );
Library->AddItem(ColorItem);
// 添加到默认组
Library->AddItemToGroup(ColorItem, Library->GetDefaultGroupId());
```

**程序化控制显示的图像**（假设标签页已打开）：

```cpp
// 将左侧图像设置为某个资产
FAssetData AssetData = ...; // 从内容浏览器获取
IMediaViewerModule::Get().SetImage(UE::MediaViewer::EMediaImageViewerPosition::First, AssetData);
```

### 进阶用法

**自定义动态组**：创建一个动态生成项目的组，例如根据当前场景中的 Actor 列表动态更新。

```cpp
class FMyDynamicGroup : public UE::MediaViewer::FMediaViewerLibraryDynamicGroup
{
public:
    FMyDynamicGroup(const TSharedRef<UE::MediaViewer::IMediaViewerLibrary>& InLibrary)
        : FMediaViewerLibraryDynamicGroup(InLibrary,
            FText::FromString("Custom Group"),
            FText::FromString("Items generated dynamically"),
            FGenerateItems::CreateStatic(&FMyDynamicGroup::GenerateItems))
    {}

protected:
    static TArray<TSharedRef<UE::MediaViewer::FMediaViewerLibraryItem>> GenerateItems()
    {
        TArray<TSharedRef<UE::MediaViewer::FMediaViewerLibraryItem>> Items;
        // 添加自定义项目 ...
        return Items;
    }
};

// 注册到库
IMediaViewerModule::Get().GetLibrary()->AddGroup(MakeShared<FMyDynamicGroup>(Library));
```

**使用 IMediaViewerLibraryWidget**：创建自定义库面板并将其嵌入到自己的 Editor UI 中。

```cpp
auto Widget = UE::MediaViewer::IMediaViewerLibraryWidget::FArgs Args;
Args.OnImageViewerOpened = ...; // 设置回调
// 通过模块接口创建 widget
TSharedRef<UE::MediaViewer::IMediaViewerLibraryWidget> LibraryWidget = 
    IMediaViewerModule::Get().CreateLibraryWidget(Args);
SomeParentWidget->AddSlot()[LibraryWidget->ToWidget()];
```

## Demo 示例

以下是一个完整的模块，在编辑器启动时自动打开 MediaViewer 标签页。

**MyMediaViewerModule.h**:
```cpp
#pragma once
#include "Modules/ModuleInterface.h"

class FMyMediaViewerModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
```

**MyMediaViewerModule.cpp**:
```cpp
#include "MyMediaViewerModule.h"
#include "IMediaViewerModule.h"

IMPLEMENT_MODULE(FMyMediaViewerModule, MyMediaViewerModule)

void FMyMediaViewerModule::StartupModule()
{
    if (IMediaViewerModule::IsAvailable())
    {
        IMediaViewerModule::Get().OpenTab();
    }
}

void FMyMediaViewerModule::ShutdownModule()
{
    // 清理
}
```

**MyMediaViewerModule.Build.cs**:
```csharp
using UnrealBuildTool;

public class MyMediaViewerModule : ModuleRules
{
    public MyMediaViewerModule(ReadOnlyTargetRules Target) : base(Target)
    {
        PublicDependencyModuleNames.Add("MediaViewer");
        // 其他依赖（自动包含 Core、Engine 等）
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MediaStream` | 提供媒体流处理和播放支持（MediaSource、MediaTexture 等） |
| `MediaPlayerEditor` | 提供媒体播放器编辑器相关基础设施 |
| `AppFramework` | 提供 Slate 应用框架支持（工具栏、标签页等） |

无其他特殊依赖（标准 Core/Engine/Slate 等已省略）。

## 维护状态

### 近期更新

- 2025-10-17 `d60394fd` Media Viewer: Reworked object referencing to account for level change GC and asset deletion.
- 2025-10-03 `4497b99a` Media Viewer: Fixed typo in uproperty.
- 2025-10-03 `3a055494` Media Viewer: You can now override the mip level of images.
- 2025-09-25 `74762c58` Media Viewer: Toggling the overlay while in comparison mode no longer blocks the custom image ui.
- 2025-09-23 `da14907a` Media Viewer: Scrubbing now calls Scrub instead of Seek to enable smoothing scrubbing.

### 维护评价

- **创建时间**：2025-09-23（约 0 年前，非常新的插件）。
- **最近更新**：持续有功能性更新（Mip 控制、GC 优化、UI 修复等），最近一次更新在 2025-10-17，表明项目处于**活跃开发**阶段。
- **限制**：仍在 Beta 阶段，API 可能不稳定，默认不启用。
- **推荐使用**：如果需要在编辑器内集中管理和对比媒体资源，非常推荐尝试。但由于 Beta 性质，建议在生产项目中谨慎集成，做好版本锁定。

## 相关链接

- [源码（插件根目录）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/MediaViewer)
- [官方文档](https://docs.unrealengine.com/)（目前该插件无独立文档，可参考源码）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/MediaViewer/Tests)（如果有）