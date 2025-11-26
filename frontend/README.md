# Hotel Reservations UI - Frontend

React frontend with AG Grid for interactive data visualization and filtering.

## Features

- Interactive data grid with AG Grid
- Dataset selector (3 datasets)
- Advanced filtering panel
- Real-time statistics dashboard
- Pagination and sorting
- Responsive design
- Modern UI with gradients

## Tech Stack

- **React 18**: UI framework
- **Vite**: Build tool and dev server
- **AG Grid**: High-performance data grid
- **Axios**: HTTP client
- **CSS**: Custom styling with gradients

## Setup

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Configure API URL (Optional)

Create `.env` file if your backend is not at `localhost:8000`:

```bash
VITE_API_URL=http://localhost:8000
```

### 3. Run Development Server

```bash
npm run dev
```

The app will open at `http://localhost:3000`

## Building for Production

```bash
npm run build
```

Build output will be in `dist/` folder.

To preview production build:

```bash
npm run preview
```

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── DataGrid.jsx          # AG Grid component
│   │   ├── DataGrid.css
│   │   ├── FilterPanel.jsx       # Filter controls
│   │   ├── FilterPanel.css
│   │   ├── StatsPanel.jsx        # Statistics display
│   │   └── StatsPanel.css
│   ├── api/
│   │   └── client.js             # API client
│   ├── App.jsx                   # Main app component
│   ├── App.css
│   ├── main.jsx                  # Entry point
│   └── index.css                 # Global styles
├── public/
├── index.html
├── package.json
├── vite.config.js
└── README.md
```

## Components

### DataGrid
- Displays paginated data from selected dataset
- Supports sorting and filtering
- Manual pagination with page size control
- Responsive column widths

### FilterPanel
- Collapsible filter panel
- Price range filter
- Booking status checkboxes
- Date filters (year, month)
- Apply/Clear actions
- Shows active filter count

### StatsPanel
- Real-time statistics from backend
- Total records, average price
- Cancellation rate
- Lead time, stay duration
- Unique hotels/countries/segments
- Colorful gradient cards

## Features in Detail

### Dataset Selection
- Switch between 3 datasets
- Shows row count for each
- Auto-loads statistics

### Filtering
- Price range (min/max)
- Booking status (Canceled/Not Canceled)
- Arrival year and month
- Filters applied on button click
- Clear all filters option

### Pagination
- Configurable page size (50-1000)
- First/Previous/Next/Last navigation
- Shows current page and total pages
- Shows filtered record count

### AG Grid Features
- Sortable columns (click header)
- Resizable columns (drag edge)
- Number formatting for prices
- Cell text selection
- Smooth animations

## API Integration

The frontend connects to FastAPI backend at `http://localhost:8000`:

- `GET /api/datasets` - List datasets
- `GET /api/data/{dataset}` - Get paginated data with filters
- `GET /api/stats/{dataset}` - Get statistics

See `src/api/client.js` for full API client implementation.

## Customization

### Colors
Edit CSS custom properties in component CSS files.

### API URL
Set `VITE_API_URL` environment variable.

### Page Sizes
Edit options in `DataGrid.jsx` line ~98.

### Filters
Add more filters in `FilterPanel.jsx` and update API client.

## Troubleshooting

### Backend Not Connecting
- Ensure backend is running on port 8000
- Check CORS settings in backend
- Verify API_BASE_URL in `src/api/client.js`

### AG Grid Not Displaying
- Check browser console for errors
- Ensure AG Grid CSS is imported
- Verify data structure matches column definitions

### Slow Loading
- Reduce page size
- Add database indexes
- Enable backend caching

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)

## License

Part of CS236 Project

