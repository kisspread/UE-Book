# Windows Virtual Keyboard

> Virtual Keyboard support for Windows. Requires Windows 11 26100.5061 or later

| 属性 | 值 |
|---|---|
| 分类 | Input Devices |
| 默认启用 | false |
| 包含内容 | false |
| 模块 | WinVirtualKeyboard (RuntimeNoCommandlet) |
| 创建时间 | 2025-08-18 |
| 年龄标签 | 🆕 |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Windows/WinVirtualKeyboard) | |

## 用途

WinVirtualKeyboard 插件为 Windows 平台提供了 **软键盘（虚拟键盘）支持**，解决了在没有物理键盘的 Windows 设备上（如平板电脑、掌机、触屏一体机）无法输入文字的问题。

插件通过 Windows 的 `CoreInputView` API（属于 `Windows.UI.ViewManagement.Core` 命名空间）来显示和隐藏系统虚拟键盘。它专门使用 **Gamepad 模式**（`CoreInputViewKind::Gamepad`，值为 7），这意味着它主要面向使用手柄或触屏交互的场景，而非桌面键鼠用户。

插件通过 UE5 的 Modular Feature 系统注册为 `IPlatformTextFieldFactory`，当 Slate 的文字输入控件（如 `SEditableTextBox`、`SMultiLineEditableText`）需要弹出虚拟键盘时，引擎会自动调用此插件的实现。

### 关键技术细节

- **操作系统要求**: Windows 11 Build 26100.5061 或更高版本（即 Windows 11 24H2 更新）
- **API**: 使用 `Windows.UI.ViewManagement.Core.CoreInputView` 的 WinRT API
- **两种实现方式**: 代码中保留了 COM（WRL）和 C++/WinRT 两种实现路径，通过 `WITH_CPPWINRT` 编译宏切换，当前默认使用 COM 方式
- **Platform 限制**: 仅支持 Win64

## 使用场景

- 你在开发 Windows 平板/掌机游戏，需要软键盘输入文字（如聊天框、玩家名称输入）
- 你的游戏运行在 Steam Deck 或类似触屏 Windows 设备上，需要手柄模式的虚拟键盘
- 你在开发 Xbox 应用的 Windows 版本，需要兼容手柄输入的虚拟键盘

## 启用方式

此插件**默认禁用**且标记为 **Beta 版本**。需要手动启用：

### 编辑器中启用

1. 打开 **Edit → Plugins**
2. 搜索 "Windows Virtual Keyboard"
3. 勾选启用，重启编辑器

### 代码中启用

在项目的 `.uproject` 文件中添加：

```json
{
    "Plugins": [
        {
            "Name": "WinVirtualKeyboard",
            "Enabled": true
        }
    ]
}
```

或在项目的 `DefaultEngine.ini` 中：

```ini
[/Script/WindowsRuntimeSettings.WindowsRuntimeSettings]
+EnabledPlugins=WinVirtualKeyboard
```

## 蓝图用法

此插件**没有暴露任何蓝图节点**。它完全通过引擎内部的 Modular Feature 系统工作，无需用户手动调用。只要插件被启用，Slate 的文字输入控件在需要时会自动触发虚拟键盘的显示/隐藏。

### 自动生效的场景

| 控件 | 触发时机 |
|---|---|
| `SEditableTextBox` | 获得焦点时自动弹出键盘 |
| `SMultiLineEditableText` | 获得焦点时自动弹出键盘 |
| `SSpinBox` | 获得焦点时弹出数字键盘 |
| `UEditableText`（蓝图） | 获得焦点时自动弹出键盘 |
| `UEditableTextBox`（蓝图） | 获得焦点时自动弹出键盘 |

## C++ 用法

此插件的设计理念是**启用即生效**，不需要用户编写任何 C++ 代码。插件在 `StartupModule` 时通过 `IModularFeatures` 注册自己为 `IPlatformTextFieldFactory`，引擎的 Slate 框架会自动发现并使用它。

### 工作原理

```
用户点击输入框 → Slate 检测到需要虚拟键盘
    → IPlatformTextFieldFactory::TryCreateInstance()
    → WinVirtualKeyboard 插件返回 FWindowsPlatformTextField
    → 调用 ShowVirtualKeyboard(true, ...)
    → Windows CoreInputView::TryShow(Gamepad)
    → 系统虚拟键盘弹出
```

### 如果你需要自定义虚拟键盘行为

如果你需要覆盖默认的虚拟键盘实现，可以参考此插件的模式：

```cpp
// 引入头文件
#include "Framework/Application/IPlatformTextField.h"
#include "Features/IModularFeatures.h"

// 创建自定义实现
class FMyPlatformTextField : public IPlatformTextField
{
public:
    virtual void ShowVirtualKeyboard(bool bShow, int32 UserIndex, 
        TSharedPtr<IVirtualKeyboardEntry> TextEntryWidget) override
    {
        // 自定义虚拟键盘逻辑
    }
};

// 创建工厂
class FMyTextFieldFactory : public IPlatformTextFieldFactory
{
public:
    virtual void StartupModule() override
    {
        IModularFeatures::Get().RegisterModularFeature(
            IPlatformTextFieldFactory::FeatureName, this);
    }
    
    virtual TUniquePtr<IPlatformTextField> CreateInstance() override
    {
        return MakeUnique<FMyPlatformTextField>();
    }
};
```

### 编译依赖

如果你的模块需要与虚拟键盘系统交互，在 `Build.cs` 中添加：

```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "Core",
    "Slate"
});
```

## Demo 示例

此插件是最小化的运行时模块，没有单独的 Demo。以下是验证插件是否工作的最简步骤：

1. 启用插件
2. 创建一个包含 `Editable Text Box` 控件的 UMG Widget
3. 在 Windows 11 设备上打包运行
4. 点击输入框 → 应该看到系统虚拟键盘弹出

**注意**: 在编辑器中运行可能不会触发虚拟键盘，因为编辑器自身处理了文本输入。建议打包后测试。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | 引擎核心模块，提供模块系统基础 |
| `Slate` | UI 框架，提供 `IPlatformTextField` 接口 |
| `WindowsApp.lib` | Windows 系统库，提供 WinRT/COM 运行时支持 |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-10-17 | `f09561780f7a` | remove incorrect code block | 移除了错误的代码段，可能是文档或注释中的误写 |
| 2025-08-18 | `8931b9676a41` | static analysis fixes | 静态分析修复，代码质量改进 |
| 2025-08-18 | `5a2627102af0` | Experimental Windows Virtual Keyboard plugin | 插件首次提交，标记为实验性 |

### 维护评价

- **创建时间**: 2025-08-18，非常新的插件
- **状态**: Beta（`IsBetaVersion: true`），实验性质
- **代码量**: 仅 1 个 .cpp 文件，187 行，极度精简
- **最后更新**: 2025-10-17，距今约 7 个月
- **更新频率**: 低，但考虑到代码量极小，这属于正常情况

**⚠️ 注意事项**:
- 此插件标记为 Beta，API 和行为可能在后续版本中变化
- 仅支持 Win64，不适用于跨平台项目
- 要求 Windows 11 26100.5061+，较旧的 Windows 版本无法使用
- 目前默认禁用，需要手动启用

**推荐**: 如果你的目标平台是 Windows 且需要支持软键盘输入（平板/掌机场景），可以启用此插件。但要注意它仍处于 Beta 状态，建议在正式项目中做好 fallback 处理。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Windows/WinVirtualKeyboard)
- [IPlatformTextField 接口](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Source/Runtime/Slate/Public/Framework/Application/IPlatformTextField.h)
- [Windows CoreInputView 文档](https://learn.microsoft.com/en-us/uwp/api/windows.ui.viewmanagement.core.coreinputview)
