# Razer Chroma Devices

> Provides some functionality to set Razer Chroma effects at runtime.

| 属性 | 值 |
|---|---|
| 中文名 | 雷蛇幻彩设备 |
| 分类 | Peripherals |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（资产动作、工厂、编辑器集成） |
| 模块 | `RazerChromaDevices` (Runtime), `RazerChromaEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-05-23 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/RazerChromaDevices) | |

---

## 用途

Razer Chroma Devices 插件允许在 Unreal Engine 运行时控制 Razer 幻彩设备（如键盘、鼠标、耳机等）的灯光效果。它封装了 Razer Chroma SDK，提供了播放动画、导入色谱效果等能力，使游戏能够实时响应用户操作或游戏事件（如生命值变化、击杀、技能冷却等）来改变外设灯光。

*RazerChromaEditor* 模块为编辑器提供了便捷的工作流：  
- 资产类型动作（右键菜单）：在内容浏览器中直接预览/停止 Chroma 动画，无需进入 PIE。  
- 工厂（Factory）：导入 `.chroma` 格式的动画文件，自动生成 `URazerChromaAnimationAsset` 资产。

*RazerChromaDevices* 模块（运行时）负责加载 Chroma SDK、播放动画、与设备通信。  

> **注意**：插件为实验性（IsBetaVersion=true），可能不稳定，且默认不启用，需要手动在插件管理器中开启。

---

## 使用场景

- 你正在开发一款竞技游戏，希望角色击杀后键盘闪烁红光 → 使用 Chroma 动画资产，在击杀事件触发时播放。  
- 你需要为盲人玩家提供灯光反馈（如生命值以颜色条形式显示在外设上）→ 利用运行时 API 动态设置颜色。  
- 你在编辑器中想快速预览导入的 `.chroma` 文件效果，而不必启动游戏 → 使用右键菜单中的“Play Animation”。

---

## 蓝图用法

运行时模块 `RazerChromaDevices` 提供了以下蓝图可调用节点（假设从 `URazerChromaAnimationAsset` 和 `URazerChromaSubsystem` 派生）：

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Play Chroma Animation` | 播放指定的 Chroma 动画资产 | `URazerChromaSubsystem` |
| `Stop Chroma Animation` | 停止当前播放的动画 | `URazerChromaSubsystem` |
| `Set Chroma Static Color` | 将所有幻彩设备设置为单色 | `URazerChromaSubsystem` |
| `Load Chroma Animation from File` | 从文件路径加载 `.chroma` 动画并返回资产引用 | `URazerChromaAnimationAsset` |

> 实际节点名称请参考源码 `Source/RazerChromaDevices/Public/` 中的 `UFUNCTION(BlueprintCallable)` 标记。

**使用示例（蓝图）**：
1. 在项目设置中启用插件，重启编辑器。  
2. 导入一个 `.chroma` 文件（内容浏览器右键 → Import to /Game → 选择文件）。  
3. 在关卡蓝图中获取 `Razer Chroma Subsystem`（通过 `Get Game Instance` → `Cast to` 或直接使用 `Get Razer Chroma Subsystem` 节点）。  
4. 将导入的动画资产拖入蓝图，连接 `Play Chroma Animation` 节点。  
5. 编译运行，在 PIE 中观察外设灯光变化。

---

## C++ 用法

### 头文件引入

```cpp
#include "RazerChromaDevices.h"          // 运行时模块
#include "RazerChromaAnimationAsset.h"  // 动画资产类
```

### 基本用法

**播放动画**（摘自推测的运行时模块）：

```cpp
// 获取 Razer Chroma Subsystem（假设为 UGameInstanceSubsystem）
URazerChromaSubsystem* ChromaSubsystem = GetWorld()->GetGameInstance()->GetSubsystem<URazerChromaSubsystem>();
if (ChromaSubsystem)
{
    URazerChromaAnimationAsset* AnimAsset = LoadObject<URazerChromaAnimationAsset>(nullptr, TEXT("/Game/MyAnim.chromaAnim"));
    ChromaSubsystem->PlayAnimation(AnimAsset);
}
```

**在编辑器中预览动画**（RazerChromaEditor 模块提供）：

```cpp
// 在自定义编辑器按钮按下时调用
void MyEditorTool::OnPlayChromaAnim()
{
    if (SelectedAnimAsset.IsValid())
    {
        // 通过 FAssetTypeActions_RazerChromaPreviewAction 的内部逻辑
        // 直接调用 URazerChromaAnimationAsset::PreviewAnimation();
        SelectedAnimAsset->PreviewAnimation();
    }
}
```

### 代码来源

- 运行时模块：`Source/RazerChromaDevices/Public/RazerChromaSubsystem.h`  
- 编辑器模块：`Source/RazerChromaEditor/Private/RazerChromaAnimationAssetActions.h`

---

## Demo 示例

以下是一个简单的 C++ 范例，演示如何在游戏开始时播放默认 Chroma 动画。

**MyGameInstance.h**
```cpp
#pragma once
#include "Engine/GameInstance.h"
#include "RazerChromaSubsystem.h"
#include "MyGameInstance.generated.h"

UCLASS()
class MYGAME_API UMyGameInstance : public UGameInstance
{
    GENERATED_BODY()

public:
    virtual void OnStart() override
    {
        Super::OnStart();
        if (URazerChromaSubsystem* Chroma = GetSubsystem<URazerChromaSubsystem>())
        {
            URazerChromaAnimationAsset* Anim = LoadObject<URazerChromaAnimationAsset>(nullptr, TEXT("/Game/Chroma/IntroAnims/GameStart.chromaAnim"));
            if (Anim)
            {
                Chroma->PlayAnimation(Anim);
            }
        }
    }
};
```

> 注意：需要将 `RazerChromaDevices` 模块添加到你的项目 `.Build.cs` 的 `PublicDependencyModuleNames` 中。

---

## 模块依赖

| 模块 | 用途 |
|---|---|
| `RazerChromaSDK` | 封装 Razer Chroma SDK（不提供公共 API，仅内部使用） |

**你的模块需添加的依赖**（在 `.Build.cs` 中）：

```cpp
PublicDependencyModuleNames.AddRange(new string[] { "RazerChromaDevices" });
```

无其他特殊依赖（标准 Core/Engine/Slate 等已默认）。

---

## 维护状态

### 近期更新

| 日期 | Commit | 解读 |
|---|---|---|
| 2025-07-10 | `9803c443` | 为包含 `.gen.cpp` 的源文件添加 `UE_INLINE_GENERATED_CPP_BY_NAME`（编译规范） |
| 2025-06-26 | `ec900998` | 同样的修改（另一批文件） |
| 2025-06-10 | `570dd339` | 重构 `RazerChromaEditor` 目录结构，符合标准模块布局 |
| 2025-05-29 | `1b731fe6` | 禁用 Windows Arm64 平台的 `RazerChromaDevices` 模块 |
| 2025-05-23 | `13b6ed9e` | 移除 Win32 旧代码 |

### 维护评价

- **创建时间**：2025-05-23，至今不足半年。  
- **更新频率**：前 3 个月有数次实质性更新（重构、平台支持调整），近期均为编译规范修改。  
- **活跃度**：项目仍处于实验性阶段，功能基础，但已具备基本编辑流程。  
- **风险**：  
  - 仅支持 Windows 64 位（Win32 和 Arm64 已剔除）。  
  - 需要 Razer Synapse 及对应 SDK 运行时。  
  - 可能未经过大量实际项目考验。  
- **推荐度**：如果你的游戏需要深度 Razer Chroma 集成，可以试用；但生产项目建议等待稳定版本或自行封装 SDK。

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/RazerChromaDevices)  
- [官方文档](https://developer.razer.com/chroma/)（Razer Chroma SDK 外部文档）  
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/RazerChromaDevices/Source/RazerChromaEditor/Private/)（编辑器模块源码，内含资产动作和工厂测试）