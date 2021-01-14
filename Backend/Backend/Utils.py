from PIL import Image
import matplotlib.pyplot as plt
from matplotlib.patheffects import Stroke, Normal
import numpy as np
from scipy.ndimage.filters import gaussian_filter

from fastai1.fastai.basic_train import Learner


def fig2data(fig):
    """
    @brief Convert a Matplotlib figure to a 4D numpy array with RGBA channels and return it
    @param fig a matplotlib figure
    @return a numpy 3D array of RGBA values
    """
    # draw the renderer
    fig.canvas.draw()

    # Get the RGBA buffer from the figure
    w, h = fig.canvas.get_width_height()
    buf = np.fromstring(fig.canvas.tostring_argb(), dtype=np.uint8)
    buf.shape = (w, h, 4)

    # canvas.tostring_argb give pixmap in ARGB mode. Roll the ALPHA channel to have it in RGBA mode
    buf = np.roll(buf, 3, axis=2)
    return buf


def fig2img(fig):
    """
    @brief Convert a Matplotlib figure to a PIL Image in RGBA format and return it
    @param fig a matplotlib figure
    @return a Python Imaging Library ( PIL ) image
    """
    # put the figure pixmap into a numpy array
    buf = fig2data(fig)
    w, h, d = buf.shape
    return Image.frombytes("RGBA", (w, h), buf.tostring())


def draw_text(ax, xy, txt, sz=14):
    text = ax.text(*xy, txt, verticalalignment='top', color='white', fontsize=sz, weight='bold')
    draw_outline(text, 1)


def draw_outline(matplt_plot_obj, lw):
    matplt_plot_obj.set_path_effects([Stroke(linewidth=lw, foreground='black'), Normal()])


def show_img(im, figsize=None, ax=None, alpha=1, cmap=None):
    if not ax:
        fig, ax = plt.subplots(figsize=figsize)
    ax.imshow(im, alpha=alpha, cmap=cmap)
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)
    return ax


def visualize_attention(im, pred, alphas, denorm, vocab, att_size=7, thresh=0., sz=224, return_fig_as_PIL_image=False):
    cap_len = len(pred)
    alphas = alphas.view(-1, 1, att_size, att_size).cpu().data.numpy()
    alphas = np.maximum(thresh, alphas)
    alphas -= alphas.min()
    alphas /= alphas.max()

    figure, axes = plt.subplots(cap_len // 5 + 1, 5, figsize=(12, 8))

    for i, ax in enumerate(axes.flat):
        if i <= cap_len:
            ax = show_img(denorm(im), ax=ax)
            if i > 0:
                mask = np.array(Image.fromarray(alphas[i - 1, 0]).resize((sz, sz)))
                blurred_mask = gaussian_filter(mask, sigma=8)
                show_img(blurred_mask, ax=ax, alpha=0.5, cmap='afmhot')
                draw_text(ax, (0, 0), vocab.itos[pred[i - 1]])
        else:
            ax.axis('off')
    plt.tight_layout()

    if return_fig_as_PIL_image:
        return fig2img(figure)


# def plot_loss_change(sched, sma=1, n_skip=20, y_lim=(-0.01, 0.01)):
#     """
#     Plots rate of change of the loss function.
#     Parameters:
#         sched - learning rate scheduler, an instance of LR_Finder class.
#         sma - number of batches for simple moving average to smooth out the curve.
#         n_skip - number of batches to skip on the left.
#         y_lim - limits for the y axis.
#     """
#     derivatives = [0] * (sma + 1)
#     for i in range(1 + sma, len(learn.sched.lrs)):
#         derivative = (learn.sched.losses[i] - learn.sched.losses[i - sma]) / sma
#         derivatives.append(derivative)
#
#     plt.ylabel("d/loss")
#     plt.xlabel("learning rate (log scale)")
#     plt.plot(learn.sched.lrs[n_skip:], derivatives[n_skip:])
#     plt.xscale('log')
#     plt.ylim(y_lim)


def find_appropriate_lr(model: Learner, lr_diff: int = 15, loss_threshold: float = .05, adjust_value: float = 1,
                        plot: bool = False) -> float:
    # Run the Learning Rate Finder
    model.lr_find()

    # Get loss values and their corresponding gradients, and get lr values
    losses = np.array(model.recorder.losses)
    assert (lr_diff < len(losses))
    loss_grad = np.gradient(losses)
    lrs = model.recorder.lrs

    # Search for index in gradients where loss is lowest before the loss spike
    # Initialize right and left idx using the lr_diff as a spacing unit
    # Set the local min lr as -1 to signify if threshold is too low
    r_idx = -1
    l_idx = r_idx - lr_diff
    while (l_idx >= -len(losses)) and (abs(loss_grad[r_idx] - loss_grad[l_idx]) > loss_threshold):
        local_min_lr = lrs[l_idx]
        r_idx -= 1
        l_idx -= 1

    lr_to_use = local_min_lr * adjust_value

    if plot:
        # plots the gradients of the losses in respect to the learning rate change
        plt.plot(loss_grad)
        plt.plot(len(losses) + l_idx, loss_grad[l_idx], markersize=10, marker='o', color='red')
        plt.ylabel("Loss")
        plt.xlabel("Index of LRs")
        plt.show()

        plt.plot(np.log10(lrs), losses)
        plt.ylabel("Loss")
        plt.xlabel("Log 10 Transform of Learning Rate")
        loss_coord = np.interp(np.log10(lr_to_use), np.log10(lrs), losses)
        plt.plot(np.log10(lr_to_use), loss_coord, markersize=10, marker='o', color='red')
        plt.show()

    return lr_to_use