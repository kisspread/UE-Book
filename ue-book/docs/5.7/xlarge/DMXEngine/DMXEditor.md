# DMX Engine

> Functionality and assets for communication with DigitalMultiplexer (DMX) enabled devices

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `DMXBlueprintGraph` (UncookedOnly), `DMXEditor` (Editor), `DMXRuntime` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2020-02-19 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DMX/DMXEngine) | |

## 用途

DMX Engine 插件为 Unreal Engine 提供了与 DMX (Digital Multiplex) 协议设备进行通信的完整框架。它解决的核心问题是**在虚拟制作（Virtual Production）流程中，将 UE5 的灯光、材质、蓝图系统与真实的 DMX 灯光控制台、灯具等硬件设备进行实时、双向的集成**。

该插件不仅仅是一个通信协议库，它提供了一个完整的编辑器和工作流，用于：
1.  **定义和管理 DMX 设备**：通过 `DMXLibrary` 资产来组织 `FixtureType`（设备类型，定义了设备的功能和通道映射）和 `FixturePatch`（设备实例，定义了设备在 DMX 宇宙中的地址）。
2.  **发送和接收 DMX 数据**：在运行时（Runtime）通过蓝图或 C++ 控制设备，或从设备接收数据。
3.  **支持行业标准**：支持导入/导出 GDTF (General Device Type Format) 和 MVR (My Virtual Rig) 文件，便于与灯光设计软件（如 grandMA3, Vectorworks）交换数据。
4.  **提供可视化工具**：内置通道监视器、活动监视器、冲突检测等工具，方便调试和监控 DMX 流量。

简而言之，它是 UE5 虚拟制作管线中连接数字世界与物理灯光世界的桥梁。

## 使用场景

-   **虚拟演唱会/舞台剧灯光设计**：在 UE5 中预演灯光效果，并通过 DMX 协议实时控制现场的灯光设备，实现“所见即所得”。
-   **影视制作中的实时灯光控制**：在 LED 虚拟制片（Virtual Production）现场，使用 UE5 控制 LED 墙的灯光氛围，并与实体灯光设备同步。
-   **交互式装置与主题公园**：创建由游戏逻辑或观众交互驱动的灯光秀，通过 DMX 控制大量灯具。
-   **灯光设备预可视化**：在购买或搭建实体灯光设备前，在 UE5 中模拟其效果和交互。
-   **开发自定义 DMX 控制工具**：利用插件提供的 API，开发自己的 DMX 控制台界面或自动化脚本。

## 蓝图用法

DMX Engine 的蓝图功能主要集中在 `DMXRuntime` 模块中，用于运行时数据收发。`DMXEditor` 模块则主要提供编辑器内的工具和 UI。以下节点主要来自 `DMXRuntime` 模块（基于通用 API 推断，具体节点需查阅 `DMXRuntime` 模块文档）。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Send DMX` | 向指定的 DMX 宇宙和通道发送数据。 | `UDMXSubsystem` |
| `Receive DMX` | 从指定的 DMX 宇宙和通道接收数据（通常通过事件）。 | `UDMXSubsystem` |
| `Get Fixture Patch` | 根据名称或索引从 DMX Library 获取一个 Fixture Patch 引用。 | `UDMXSubsystem` |
| `Get Fixture Type` | 根据名称或索引从 DMX Library 获取一个 Fixture Type 引用。 | `UDMXSubsystem` |
| `Map DMX to Attribute` | 将原始的 DMX 通道值映射到 Fixture Type 中定义的属性（如 Dimmer, Pan, Tilt）。 | `UDMXEntityFixturePatch` |
| `Set Attribute Value` | 设置一个 Fixture Patch 的某个属性值（如设置亮度为 1.0）。 | `UDMXEntityFixturePatch` |

### 使用示例（蓝图描述）

1.  **发送 DMX 控制灯光**：
    *   在你的 Actor 蓝图中，添加一个 `DMXLibrary` 引用变量。
    *   使用 `Get Fixture Patch` 节点，通过名称（如 “WashLight_01”）获取目标灯具的 Patch。
    *   使用 `Set Attribute Value` 节点，将 “Dimmer” 属性设置为 0.8， “Color” 属性设置为红色。
    *   连接一个 `Event Tick` 或自定义事件来驱动此逻辑，实现实时控制。

2.  **接收 DMX 数据**：
    *   在 `DMXSubsystem` 上绑定 `On DMX Received` 事件。
    *   在事件处理中，使用 `Map DMX to Attribute` 节点将接收到的原始数据解析为具体的属性值（如 “Fader_1” 的值）。
    *   根据解析出的值，驱动场景中的物体（如改变灯光强度、移动物体）。

## C++ 用法

C++ 用法主要分为两部分：运行时 API（`DMXRuntime`）和编辑器工具 API（`DMXEditor`）。

### 头文件引入

```cpp
// 运行时功能
#include "DMXRuntime/Public/DMXSubsystem.h"
#include "DMXRuntime/Public/Library/DMXEntityFixturePatch.h"
#include "DMXRuntime/Public/Library/DMXEntityFixtureType.h"
#include "DMXRuntime/Public/Library/DMXLibrary.h"

// 编辑器工具功能 (仅在编辑器模块中可用)
#include "DMXEditor/Public/DMXEditorUtils.h"
```

### 基本用法

以下示例展示了如何在 C++ 中使用编辑器工具类 `FDMXEditorUtils` 来验证和操作 DMX 实体。
（来源：`Engine/Plugins/VirtualProduction/DMX/DMXEngine/Source/DMXEditor/Public/DMXEditorUtils.h`）

```cpp
#include "DMXEditorUtils.h"
#include "Library/DMXLibrary.h"
#include "Library/DMXEntityFixtureType.h"

void MyDMXEditorFunction(UDMXLibrary* MyLibrary)
{
    // 1. 验证一个新的实体名称是否有效且唯一
    FText Reason;
    FString NewName = TEXT("MyNewFixture");
    UClass* EntityClass = UDMXEntityFixtureType::StaticClass();
    bool bIsValid = FDMXEditorUtils::ValidateEntityName(NewName, MyLibrary, EntityClass, Reason);
    
    if (bIsValid)
    {
        // 2. 创建一个新的 Fixture Type (通常通过工厂或编辑器UI，这里仅为演示API)
        // UDMXEntityFixtureType* NewType = UDMXEntityFixtureType::CreateFixtureType(MyLibrary, NewName);
        
        // 3. 检查两个 Fixture Type 是否几乎相同（忽略名称和ID）
        UDMXEntityFixtureType* TypeA = /* ... */;
        UDMXEntityFixtureType* TypeB = /* ... */;
        bool bAreIdentical = FDMXEditorUtils::AreFixtureTypesIdentical(TypeA, TypeB);
        
        // 4. 复制实体到剪贴板
        TArray<UDMXEntity*> EntitiesToCopy = { TypeA };
        FDMXEditorUtils::CopyEntities(MoveTemp(EntitiesToCopy));
        
        // 5. 检查是否可以从剪贴板粘贴
        if (FDMXEditorUtils::CanPasteEntities(MyLibrary))
        {
            // 6. 从剪贴板创建实体
            TArray<UDMXEntity*> PastedEntities = FDMXEditorUtils::CreateEntitiesFromClipboard(MyLibrary);
        }
    }
}
```

### 进阶用法

结合 `DMXFixtureTypeSharedData` 和 `DMXFixturePatchSharedData` 来管理编辑器中的选择状态，这对于开发自定义的 DMX 编辑器面板非常有用。
（来源：`Engine/Plugins/VirtualProduction/DMX/DMXEngine/Source/DMXEditor/Public/DMXFixtureTypeSharedData.h` 和 `DMXFixturePatchSharedData.h`）

```cpp
#include "DMXFixtureTypeSharedData.h"
#include "DMXFixturePatchSharedData.h"
#include "DMXEditor.h"

void MyCustomEditorPanel::OnSelectionChanged()
{
    // 假设我们有一个指向 DMX Editor 实例的弱指针
    TWeakPtr<FDMXEditor> DMXEditorPtr = /* ... */;
    
    if (DMXEditorPtr.IsValid())
    {
        // 获取 Fixture Type 的共享数据（管理类型编辑器的选择）
        TSharedPtr<FDMXFixtureTypeSharedData> FixtureTypeSharedData = DMXEditorPtr.Pin()->GetFixtureTypeSharedData();
        if (FixtureTypeSharedData.IsValid())
        {
            // 获取当前选中的 Fixture Type
            const TArray<TWeakObjectPtr<UDMXEntityFixtureType>>& SelectedTypes = FixtureTypeSharedData->GetSelectedFixtureTypes();
            
            // 获取当前选中的模式索引
            const TArray<int32>& SelectedModeIndices = FixtureTypeSharedData->GetSelectedModeIndices();
            
            // 根据选择更新你的UI...
        }
        
        // 获取 Fixture Patch 的共享数据（管理 Patch 编辑器的选择）
        TSharedPtr<FDMXFixturePatchSharedData> FixturePatchSharedData = DMXEditorPtr.Pin()->GetFixturePatchSharedData();
        if (FixturePatchSharedData.IsValid())
        {
            // 获取当前选中的宇宙
            int32 SelectedUniverse = FixturePatchSharedData->GetSelectedUniverse();
            
            // 获取当前选中的 Fixture Patch
            const TArray<TWeakObjectPtr<UDMXEntityFixturePatch>>& SelectedPatches = FixturePatchSharedData->GetSelectedFixturePatches();
            
            // 根据选择更新你的UI...
        }
    }
}
```

## Demo 示例

以下是一个最小化的编辑器工具模块示例，它注册了一个简单的菜单命令来打印当前 DMX Library 中 Fixture Type 的数量。
（注意：此示例仅适用于编辑器环境，需要将模块类型设置为 `Editor`）

**MyDMXEditorTool.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"

class FMyDMXEditorToolModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

private:
    void RegisterMenus();
    void PrintFixtureTypeCount();
};
```

**MyDMXEditorTool.cpp**
```cpp
#include "MyDMXEditorTool.h"
#include "DMXEditorUtils.h"
#include "Library/DMXLibrary.h"
#include "ToolMenus.h"
#include "ContentBrowserModule.h"

#define LOCTEXT_NAMESPACE "FMyDMXEditorToolModule"

void FMyDMXEditorToolModule::StartupModule()
{
    UToolMenus::RegisterStartupCallback(FSimpleMulticastDelegate::FDelegate::CreateRaw(this, &FMyDMXEditorToolModule::RegisterMenus));
}

void FMyDMXEditorToolModule::ShutdownModule()
{
    UToolMenus::UnRegisterStartupCallback(this);
    UToolMenus::UnregisterOwner(this);
}

void FMyDMXEditorToolModule::RegisterMenus()
{
    // 在内容浏览器的右键菜单中添加一个选项
    FToolMenuOwnerScoped OwnerScoped(this);
    UToolMenu* Menu = UToolMenus::Get()->ExtendMenu("ContentBrowser.AssetContextMenu");
    FToolMenuSection& Section = Menu->FindOrAddSection("GetAssetActions");
    
    Section.AddMenuEntry(
        "PrintDMXFixtureTypeCount",
        LOCTEXT("PrintDMXFixtureTypeCount", "Print Fixture Type Count"),
        LOCTEXT("PrintDMXFixtureTypeCountTooltip", "Prints the number of Fixture Types in the selected DMX Library to the output log."),
        FSlateIcon(),
        FUIAction(FExecuteAction::CreateRaw(this, &FMyDMXEditorToolModule::PrintFixtureTypeCount))
    );
}

void FMyDMXEditorToolModule::PrintFixtureTypeCount()
{
    // 获取内容浏览器中选中的资产
    FContentBrowserModule& ContentBrowserModule = FModuleManager::LoadModuleChecked<FContentBrowserModule>("ContentBrowser");
    TArray<FAssetData> SelectedAssets = ContentBrowserModule.Get().GetSelectedAssets();
    
    for (const FAssetData& Asset : SelectedAssets)
    {
        // 检查是否是 DMXLibrary 资产
        if (Asset.GetClass() == UDMXLibrary::StaticClass())
        {
            UDMXLibrary* Library = Cast<UDMXLibrary>(Asset.GetAsset());
            if (Library)
            {
                // 使用 DMXEditorUtils 获取所有 Fixture Type
                TArray<UObject*> AllFixtureTypes;
                FDMXEditorUtils::GetAllAssetsOfClass(UDMXEntityFixtureType::StaticClass(), AllFixtureTypes);
                
                // 过滤出属于当前 Library 的类型
                int32 Count = 0;
                for (UObject* Obj : AllFixtureTypes)
                {
                    if (UDMXEntityFixtureType* Type = Cast<UDMXEntityFixtureType>(Obj))
                    {
                        if (Type->GetParentLibrary() == Library)
                        {
                            Count++;
                        }
                    }
                }
                
                UE_LOG(LogTemp, Log, TEXT("DMX Library '%s' contains %d Fixture Types."), *Library->GetName(), Count);
            }
        }
    }
}

#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(FMyDMXEditorToolModule, MyDMXEditorTool)
```

## 模块依赖

要使用 `DMXEditor` 模块的功能（如 `FDMXEditorUtils`），你的模块需要在 `.Build.cs` 文件中添加以下依赖。`DMXRuntime` 是核心运行时模块，通常也需要依赖。

| 模块 | 用途 |
|---|---|
| `DMXRuntime` | DMX 核心运行时库，包含所有实体类、子系统和通信逻辑。 |
| `DMXEditor` | DMX 编辑器工具、UI 和工厂类。仅在编辑器模块中依赖。 |
| `PropertyEditor` | 用于自定义 DMX 实体属性在细节面板中的显示。 |
| `EditorStyle` | 提供编辑器 UI 的样式和图标。 |
| `AssetRegistry` | 用于资产查找和管理，如 `FDMXEditorUtils::GetAllAssetsOfClass`。 |

## 维护状态

### 近期更新

```
- 2d00e8bcc084 DMX: Add missing transaction for the new Fixture Type Reset To GDTF button
- 1abddb288078 DMX: The Fixture Type Editor tab in the DMX Library now has a button to reset a Fixture Type to how it was imported from GDTF
- ed12aec9a262 DMX: Remove any uses of FORCEINLINE, replace with inline where appropriate
```

### 维护评价

DMX Engine 是一个**活跃维护中**的核心虚拟制作插件。

-   **创建时间**：约 4 年前（2020年），相对较新。
-   **近期更新**：最近的提交集中在改进 Fixture Type 编辑器的工作流（如添加“重置为GDTF”按钮）和代码质量优化（替换 `FORCEINLINE`）。这表明 Epic 仍在积极投入开发，完善用户体验和代码健壮性。
-   **功能完整性**：插件提供了从数据定义、编辑器工具到运行时通信的完整闭环，功能非常全面。
-   **行业标准支持**：支持 GDTF 和 MVR 标准，确保了与主流灯光设计软件的互操作性。
-   **推荐使用**：**强烈推荐**。对于任何涉及 DMX 灯光控制的虚拟制作项目，此插件是官方且功能完备的首选方案。它随着 UE 版本持续更新，能够很好地集成到最新的引擎特性中。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DMX/DMXEngine)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/dmx-in-unreal-engine/) (UE5 官方文档中的 DMX 章节)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DMX/DMXEngine/Tests) (如果存在)