package chat.ssc.secure.plugins;

import android.Manifest;
import android.content.Intent;
import android.net.Uri;
import android.provider.Settings;

import com.getcapacitor.JSObject;
import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.PluginMethod;
import com.getcapacitor.annotation.CapacitorPlugin;
import com.getcapacitor.annotation.Permission;
import com.getcapacitor.annotation.PermissionCallback;

/**
 * Runtime RECORD_AUDIO / CAMERA for WebRTC calls on Android WebView.
 */
@CapacitorPlugin(
    name = "SscMediaPermissions",
    permissions = {
        @Permission(alias = "microphone", strings = { Manifest.permission.RECORD_AUDIO }),
        @Permission(alias = "camera", strings = { Manifest.permission.CAMERA }),
    }
)
public class SscMediaPermissionsPlugin extends Plugin {

    @PluginMethod
    public void checkPermissions(PluginCall call) {
        call.resolve(buildPermissionState());
    }

    @PluginMethod
    public void requestPermissions(PluginCall call) {
        boolean audio = call.getBoolean("audio", true);
        boolean video = call.getBoolean("video", false);

        if (!audio && !video) {
            call.resolve(buildPermissionState());
            return;
        }

        if (audio && getPermissionState("microphone") != com.getcapacitor.PermissionState.GRANTED) {
            requestPermissionForAlias("microphone", call, "permissionsCallback");
            return;
        }
        if (video && getPermissionState("camera") != com.getcapacitor.PermissionState.GRANTED) {
            requestPermissionForAlias("camera", call, "permissionsCallback");
            return;
        }
        call.resolve(buildPermissionState());
    }

    @PermissionCallback
    private void permissionsCallback(PluginCall call) {
        boolean audio = call.getBoolean("audio", true);
        boolean video = call.getBoolean("video", false);

        if (audio && getPermissionState("microphone") != com.getcapacitor.PermissionState.GRANTED) {
            call.resolve(buildPermissionState());
            return;
        }
        if (video && getPermissionState("camera") != com.getcapacitor.PermissionState.GRANTED) {
            requestPermissionForAlias("camera", call, "permissionsCallback");
            return;
        }
        call.resolve(buildPermissionState());
    }

    @PluginMethod
    public void openAppSettings(PluginCall call) {
        Intent intent = new Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS);
        Uri uri = Uri.fromParts("package", getContext().getPackageName(), null);
        intent.setData(uri);
        intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
        getActivity().startActivity(intent);
        call.resolve();
    }

    private JSObject buildPermissionState() {
        JSObject ret = new JSObject();
        ret.put("microphone", permissionToString(getPermissionState("microphone")));
        ret.put("camera", permissionToString(getPermissionState("camera")));
        return ret;
    }

    private String permissionToString(com.getcapacitor.PermissionState state) {
        if (state == com.getcapacitor.PermissionState.GRANTED) return "granted";
        if (state == com.getcapacitor.PermissionState.DENIED) return "denied";
        return "prompt";
    }
}