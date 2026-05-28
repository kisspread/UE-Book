# Portable Object File Data Source

> Data Source plugin providing portable object (PO) file support for the Content Browser

| 属性 | 值 |
|---|---|
| 中文名 | 可移植对象文件数据源 |
| 分类 | Localization |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `PortableObjectFileDataSource` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2023-06-21 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/Localization/PortableObjectFileDataSource) | |

## 用途

此插件为 Unreal Engine 的内容浏览器（Content Browser）添加了对 **Portable Object (PO) 文件** 的原生支持。PO 文件是本地化工作流中用于存储翻译条目的标准格式。该插件使得 `.po` 文件能够像其他资产一样在内容浏览器中被识别、预览和交互，解决了内容浏览器无法直接管理本地化翻译文件的问题，简化了本地化人员的工作流程。

## 使用场景

- 你的项目需要进行多语言本地化，并且使用 `.po` 文件作为翻译源文件。
- 你希望在 Unreal Editor 的内容浏览器中直接查看和管理项目中的所有 `.po` 文件，而无需使用外部工具或手动定位。
- 你开发的其他编辑器插件或工具需要处理或显示 `.po` 文件，并希望获得与内容浏览器一致的体验。

## 蓝图用法

该插件主要通过其模块接口在 C++ 层面提供服务，未暴露任何蓝图可调用的函数（`UFUNCTION(BlueprintCallable)`）或属性。其主要功能由编辑器内容浏览器自动调用。

## C++ 用法

### 头文件引入

```cpp
#include "IPortableObjectFileDataSourceModule.h"
```

### 基本用法

该插件的核心是一个提供编辑覆盖逻辑的模块接口。以下示例展示了如何注册一个自定义的 “是否可编辑” 判断逻辑，用于拦截或控制对特定 `.po` 文件的编辑行为。

```cpp
// 来自 IPortableObjectFileDataSourceModule.h
// 注册一个覆盖处理器，用于判断 PO 文件是否可编辑
void RegisterMyPOFileEditHandler()
{
    // 获取模块接口
    IPortableObjectFileDataSourceModule& POFileModule = IPortableObjectFileDataSourceModule::Get();

    // 定义一个自定义的委托，根据文件路径判断是否可编辑
    IPortableObjectFileDataSourceModule::FCanEditFileDelegate CanEditDelegate;
    CanEditDelegate.BindLambda([](const FName InFilePath, const FString& InFilename, FText* OutErrorMsg) -> bool
    {
        // 示例逻辑：禁止编辑位于 “Archive/” 目录下的归档文件
        if (InFilePath.ToString().Contains(TEXT("Archive/")))
        {
            if (OutErrorMsg)
            {
                *OutErrorMsg = NSLOCTEXT("MyPlugin", "ArchiveFileReadOnly", "Archive files are read-only.");
            }
            return false; // 不允许编辑
        }
        return true; // 允许编辑
    });

    // 注册该委托，并保存句柄以便后续注销
    FDelegateHandle MyHandle = POFileModule.RegisterCanEditFileOverride(MoveTemp(CanEditDelegate));
    // 建议将 MyHandle 存储为类成员变量
}

// 在适当时机（如模块关闭时）注销委托
void UnregisterMyPOFileEditHandler(FDelegateHandle Handle)
{
    if (IPortableObjectFileDataSourceModule* POFileModule = IPortableObjectFileDataSourceModule::GetPtr())
    {
        POFileModule->UnregisterCanEditFileOverride(Handle);
    }
}
```

## Demo 示例

由于此插件主要服务于编辑器的 UI 层（内容浏览器），且不提供运行时功能或蓝图节点，因此通常不需要编写独立的 C++ 代码来使用它。其功能在启用插件后自动生效。

一个典型的 `Setup` 函数（在你自己的编辑器模块中）可能会这样使用其接口，以扩展编辑控制权：

```cpp
// MyEditorModule.h
#pragma once
#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"
#include "IPortableObjectFileDataSourceModule.h"

class FMyEditorModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

private:
    FDelegateHandle CanEditFileDelegateHandle;
};

// MyEditorModule.cpp
#include "MyEditorModule.h"

void FMyEditorModule::StartupModule()
{
    // 确保 PO 文件数据源模块已加载
    if (IPortableObjectFileDataSourceModule* POFileModule = IPortableObjectFileDataSourceModule::GetPtr())
    {
        // 注册一个简单的覆盖，例如允许所有编辑（实际逻辑应更复杂）
        IPortableObjectFileDataSourceModule::FCanEditFileDelegate Delegate;
        Delegate.BindLambda([](const FName, const FString&, FText*) -> bool
        {
            return true; // 允许所有编辑
        });
        CanEditFileDelegateHandle = POFileModule->RegisterCanEditFileOverride(MoveTemp(Delegate));
    }
}

void FMyEditorModule::ShutdownModule()
{
    if (IPortableObjectFileDataSourceModule* POFileModule = IPortableObjectFileDataSourceModule::GetPtr())
    {
        POFileModule->UnregisterCanEditFileOverride(CanEditFileDelegateHandle);
    }
}

IMPLEMENT_MODULE(FMyEditorModule, MyEditor)
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ContentBrowserFileDataSource` | 此插件依赖的核心插件，提供了文件数据源在内容浏览器中注册和显示的基础框架。`PortableObjectFileDataSource` 在此基础上添加了对 PO 文件类型的特定支持。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-02-19 | `96d71ab4` | [PortableObjectFileDataSource] Prevent duplicate file mounts in OnContentPathMounted | 修复了在内容路径挂载时重复挂载文件的问题，提高了稳定性。 |
| 2025-02-17 | `6a987b5c` | [Backout] - CL39851897 | 回退了某个更改。 |
| 2025-02-08 | `32a9ddcf` | [Backout] - CL39569471 | 回退了另一个更改。 |
| 2025-01-29 | `1c711383` | [Backout] - CL39518357 | 回退了第三个更改。 |
| 2025-01-28 | `fa121e49` | Fix plugin discovery during refresh and mount duplication issue in PortableObjectFileDataSourceModul | 修复了插件刷新时的发现机制以及挂载重复问题。 |

### 维护评价

该插件创建于 2023 年 6 月，相对年轻。从提交历史看，在 2025 年初有密集的维护活动，主要是为了修复“文件重复挂载”相关的问题，并包含多次回退操作，这表明开发团队正在积极解决一些底层稳定性问题。插件仍处于**活跃维护**状态，功能相对专一且稳定。

**推荐使用**。如果你的工作流涉及 PO 文件，此插件是 UE 编辑器内置的官方解决方案，能够无缝集成到内容浏览器中。尽管近期有一些稳定性修复，但核心功能是可靠的。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/Localization/PortableObjectFileDataSource)