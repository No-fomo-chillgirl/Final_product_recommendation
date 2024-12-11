import streamlit as st
import pandas as pd
import pickle
import re
import matplotlib.pyplot as plt

# Function to get recommendations based on cosine similarity
def get_recommendations(df, ma_san_pham, cosine_sim, nums=5):
    # Ensure product IDs match the indices of cosine similarity matrix
    # Find the index of the selected product in df_products
    idx = df.index[df['ma_san_pham'] == ma_san_pham].tolist()
    
    if not idx:
        print(f"No product found with ID: {ma_san_pham}")
        return pd.DataFrame()  # Return an empty DataFrame
    
    idx = idx[0]  # Get the first index if there are multiple matches
    
    # Ensure that the index is within the bounds of the cosine similarity matrix
    if idx >= len(cosine_sim):
        print(f"Index {idx} is out of bounds for cosine similarity matrix.")
        return pd.DataFrame()  # Return an empty DataFrame if index is out of bounds
    
    # Get cosine similarity scores for the selected product
    sim_scores = list(enumerate(cosine_sim[idx]))
    
    # Sort products based on similarity scores in descending order
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    
    # Exclude the first product as it's the same one we selected
    sim_scores = sim_scores[1:nums+1]
    
    # Extract the indices of the most similar products
    product_indices = [i[0] for i in sim_scores]
    
    # Return the recommended products
    return df.iloc[product_indices]

def display_recommended_products(recommended_products,df_output,cols=5):
    for i in range(0, len(recommended_products), cols):
        columns = st.columns(cols)
        for j, col in enumerate(columns):
            if i + j < len(recommended_products):
                product = recommended_products.iloc[i + j]
                with col:
                    with st.container(border=True):
                        st.image(product['hinh_anh'])
                        st.write(product['ten_san_pham'])
                        st.write("Mã sản phẩm :",product['ma_san_pham'])
                        st.write("Giá :",product['gia_ban'],' VNĐ')
                        st.write("Sao :",product['diem_trung_binh'],' ⭐')
                        luotmua = df_output[df_output['ma_san_pham']==product['ma_san_pham']].groupby('ma_san_pham',as_index=False)['ma_khach_hang'].count()
                        if len(luotmua) > 0:
                            st.write("Lượt mua: ", luotmua['ma_khach_hang'][0]," 🛒")
                        else:
                            st.write("Lượt mua: 0 🛒")
                        expander=st.expander("Mô tả")
                        truncated_description = ' '.join(product['mo_ta'].split()[:100]) + '...'
                        expander.write(truncated_description)

# Read data
df_products = pd.read_csv('data/Product.csv')
df_customer = pd.read_csv('data/Customer.csv')
df_output = pd.read_csv('data/Danh_gia1.csv')

# Load precomputed cosine similarity
with open('process/products_cosine_sim_.pkl', 'rb') as f:
    cosine_sim_new = pickle.load(f)

###### Streamlit Interface ######

    # GUI
st.title("Data Science Project")
st.write("## Product Recommendation")

menu = ["Business Objective", "Login", "Recommend Product"]
choice = st.sidebar.selectbox('Menu', menu)
st.sidebar.write("""#### Thành viên thực hiện:\n
                Trần Đăng Diệp & Vũ Thị Thanh Trúc""")
st.sidebar.write("""#### Giảng viên hướng dẫn: 
                        Khuất Thùy Phương""")
st.sidebar.write("""#### Thời gian thực hiện: 7/12/2024""")
if choice == 'Business Objective':    
    st.subheader("Business Objective")
    st.write("""
    ###### Vấn đề : Một khi đã hiểu được khách hàng và nhu cầu của họ, chúng ta xây dựng được 1 hệ thống gợi ý thông minh mang những sản phẩm phù hợp đến với khách hàng, từ đó nâng cao doanh số và trải nghiệm người dùng.
    """)  
    st.write("""###### => Yêu cầu: Xây dựng thuật toán đề xuất sản phẩm dựa trên lịch sử mua hàng.""")
    st.image('images/hasaki_banner_2.jpg', use_container_width=True)
    


elif choice == 'Login':
    user_credentials = {
        "Hoàng Anh Trần": "password1",
        "Nguyễn Lương Nhi Phương": "password2",
        "Nguyễn Thu Trang": "password3"
    }

    # Giao diện đăng nhập
    st.title("Đăng nhập")

    # Hiển thị danh sách tài khoản gợi ý
    selected_username = st.selectbox("Chọn tài khoản", options=list(user_credentials.keys()), help="Chọn tài khoản từ danh sách gợi ý.")
    # Lấy mật khẩu tương ứng từ dictionary
    selected_password = user_credentials[selected_username]

    # Tự động điền mật khẩu (hiển thị dưới dạng bảo mật)
    password = st.text_input("Nhập mật khẩu", value=selected_password, type="password")

    # Gợi ý cho người dùng
    st.info("Mật khẩu tự động được điền theo tài khoản đã chọn.")
    
    
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    if st.session_state["logged_in"]:
        st.success(f"Chào mừng {selected_username}! Bạn cần đăng nhập lại")

        # Nút đăng xuất
        if st.button("Đăng xuất"):
            st.session_state["logged_in"] = False
            st.rerun()
    else:
        # Nút đăng nhập
        if st.button("Đăng nhập"):
            # Xác thực tài khoản và mật khẩu
            if user_credentials.get(selected_username) == password:
                st.session_state["logged_in"] = True
                st.success(f"Chào mừng {selected_username}! Bạn đã đăng nhập thành công.")
                # st.experimental_rerun()

                # lấy id
                get_id = df_customer[df_customer['ho_ten']==selected_username]['ma_khach_hang'].reset_index(drop='index')[0]
                # # từ id đã có , lấy sản phẩm
                customer_products = df_output[df_output['ma_khach_hang'] == get_id]['ma_san_pham'].tolist()
                if customer_products:
                    st.write("### Sản phẩm đã mua:")
                    purchased_products = df_products[df_products['ma_san_pham'].isin(customer_products)]
                    st.write(purchased_products[['ma_san_pham', 'ten_san_pham']])

                    st.write("### Gợi ý sản phẩm liên quan:")
                    all_recommendations = pd.DataFrame()
                    for product_id in customer_products:
                        recommendations = get_recommendations(df_products, product_id, cosine_sim=cosine_sim_new, nums=3)
                        recommendations = recommendations[recommendations['diem_trung_binh'] >= 4]
                        all_recommendations = pd.concat([all_recommendations, recommendations])

                    all_recommendations = all_recommendations.drop_duplicates(subset='ma_san_pham')
                    all_recommendations = all_recommendations[~all_recommendations['ma_san_pham'].isin(customer_products)]
                    display_recommended_products(all_recommendations,df_output, cols=3)
                else:
                    st.info(f"Khách hàng **{selected_username}** chưa mua sản phẩm nào.")
            else:
                st.error("Tài khoản hoặc mật khẩu không đúng!")
           
          



    

elif choice == 'Recommend Product':
    # Step 2: Select a product and get similar product recommendations
    st.write("---")
    st.write("## Gợi ý sản phẩm tương tự")

    if 'random_products' not in st.session_state:
        st.session_state.random_products = df_products.head(n=10)

    product_options = [
        (row['ten_san_pham'], row['ma_san_pham'])
        for _, row in st.session_state.random_products.iterrows()
    ]

    selected_product = st.selectbox(
        "Chọn sản phẩm",
        options=product_options,
        format_func=lambda x: x[0]
    )

    st.write("Bạn đã chọn:", selected_product)
    st.session_state.selected_ma_san_pham = selected_product[1]

    if st.session_state.selected_ma_san_pham:
        selected_product_df = df_products[df_products['ma_san_pham'] == st.session_state.selected_ma_san_pham]

        if not selected_product_df.empty:
            st.write('#### Bạn vừa chọn:')
            st.write('### ', selected_product_df['ten_san_pham'].values[0])

            product_description = selected_product_df['mo_ta'].values[0]
            st.image(selected_product_df['hinh_anh'].values[0])
            truncated_description = ' '.join(product_description.split()[:100])
            st.write('##### Thông tin:')
            st.write(truncated_description, '...')
            st.write('#### Giá :',selected_product_df['gia_ban'].values[0],' VNĐ')
            st.write('#### Sao :',selected_product_df['diem_trung_binh'].values[0],' ⭐')
            luotmua = df_output[df_output['ma_san_pham']==selected_product_df['ma_san_pham'].values[0]].groupby('ma_san_pham',as_index=False)['ma_khach_hang'].count()
            if len(luotmua) > 0:
                st.write("### Lượt mua: ", luotmua['ma_khach_hang'][0]," 🛒")
            else:
                st.write("### Lượt mua: 0 🛒")
            st.write("## Đánh giá ")
            #get product code
            msp = selected_product_df['ma_san_pham'].values[0]
            # Vẽ biểu đồ
            paint = df_output[df_output['ma_san_pham']==msp].groupby('so_sao',as_index=False)['ma_khach_hang'].count()
            paint.rename(columns={"ma_khach_hang":"tong_so_luong"}, inplace=True)
            with st.container(border=True):
                st.write("Tổng số sao được vote từ khách hàng")
                st.bar_chart(paint, x="so_sao", y="tong_so_luong", horizontal=True)
            st.write("### Các bình luận của khách hàng ")
            for i in range(0,3):
                with st.container(border=True):
                    # get mã khách hàng
                    mkh = df_output[df_output['ma_san_pham']==msp]['ma_khach_hang'].values[i]
                    # Write
                    st.write("Khách hàng : ",df_customer[df_customer['ma_khach_hang']==mkh]['ho_ten'].values[0])
                    st.write("Bình Luận  : ",df_output[df_output['ma_san_pham']==msp]['noi_dung_binh_luan'].values[i])
                    st.write("Vote : ",df_output[df_output['ma_san_pham']==msp]['so_sao'].values[i],' ⭐')
                    st.write("Ngày bình luận : ",df_output[df_output['ma_san_pham']==msp]['ngay_binh_luan'].values[i])
            st.write('##### Các sản phẩm liên quan:')
            recommendations = get_recommendations(
                df_products,
                st.session_state.selected_ma_san_pham,
                cosine_sim=cosine_sim_new,
                nums=3
            )
            display_recommended_products(recommendations,df_output, cols=3)
        else:
            st.write(f"Không tìm thấy sản phẩm với ID: {st.session_state.selected_ma_san_pham}")
